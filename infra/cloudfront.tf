resource "aws_cloudfront_origin_access_control" "website" {
  name                              = "interactive-learning-website-oac"
  description                       = "Allows CloudFront to securely read the private website bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_public_key" "auth" {
  name        = "interactive-learning-auth-public-key"
  comment     = "Public key used to validate signed authentication cookies"
  encoded_key = file("${path.module}/keys/cloudfront-auth-public.pem")
}

resource "aws_cloudfront_key_group" "auth" {
  name    = "interactive-learning-auth-key-group"
  comment = "Trusted key group for authenticated website access"
  items   = [aws_cloudfront_public_key.auth.id]
}
