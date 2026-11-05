locals {
  auth_secret_arn = "arn:aws:secretsmanager:ap-south-2:951614973911:secret:interactive-learning/cloudfront/private-key-uQypjw"
}

data "archive_file" "auth_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/auth"
  output_path = "${path.module}/.terraform/auth-lambda.zip"
}

resource "aws_iam_role" "auth_lambda" {
  name = "interactive-learning-auth-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "auth_lambda" {
  name = "interactive-learning-auth-lambda"
  role = aws_iam_role.auth_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = local.auth_secret_arn
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:aws:logs:ap-south-2:951614973911:*"
      }
    ]
  })
}

resource "aws_lambda_function" "auth" {
  function_name    = "interactive-learning-auth"
  role             = aws_iam_role.auth_lambda.arn
  runtime          = "nodejs20.x"
  handler          = "index.handler"
  filename         = data.archive_file.auth_lambda.output_path
  source_code_hash = data.archive_file.auth_lambda.output_base64sha256
  timeout          = 10

  environment {
    variables = {
      COGNITO_DOMAIN           = "https://ap-south-2kb5kpaQta.auth.ap-south-2.amazoncognito.com"
      COGNITO_CLIENT_ID        = "322ksn2mncfa1kcj8hhlhh9i5"
      REDIRECT_URI             = "https://dwn2n2k97ubpf.cloudfront.net/auth/callback.html"
      SECRET_ARN               = local.auth_secret_arn
      CLOUDFRONT_DOMAIN        = "dwn2n2k97ubpf.cloudfront.net"
      CLOUDFRONT_PUBLIC_KEY_ID = aws_cloudfront_public_key.auth.id
    }
  }
}

resource "aws_apigatewayv2_api" "auth" {
  name          = "interactive-learning-auth"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins     = ["https://dwn2n2k97ubpf.cloudfront.net"]
    allow_methods     = ["POST", "OPTIONS"]
    allow_headers     = ["content-type"]
    allow_credentials = true
  }
}

resource "aws_apigatewayv2_integration" "auth" {
  api_id                 = aws_apigatewayv2_api.auth.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.auth.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "auth" {
  api_id    = aws_apigatewayv2_api.auth.id
  route_key = "POST /session"
  target    = "integrations/${aws_apigatewayv2_integration.auth.id}"
}

resource "aws_apigatewayv2_stage" "auth" {
  api_id      = aws_apigatewayv2_api.auth.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "auth_api" {
  statement_id  = "AllowAuthApiInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.auth.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.auth.execution_arn}/*/*"
}
