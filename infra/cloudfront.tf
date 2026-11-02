resource "aws_cloudfront_origin_access_control" "website" {
  name                              = "interactive-learning-website-oac"
  description                       = "Allows CloudFront to securely read the private website bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}