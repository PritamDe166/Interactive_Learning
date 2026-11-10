resource "aws_cloudfront_function" "auth_gate" {
  name    = "interactive-learning-auth-gate"
  comment = "Redirect viewers without valid authentication cookies to login"
  runtime = "cloudfront-js-2.0"
  publish = true

  code = <<-CODE
    function handler(event) {
      var request = event.request;
      var cookies = request.cookies || {};

      if (!cookies['CloudFront-Policy'] ||
          !cookies['CloudFront-Signature'] ||
          !cookies['CloudFront-Key-Pair-Id']) {
        return {
          statusCode: 302,
          statusDescription: 'Found',
          headers: {
            location: { value: '/login.html' },
            'cache-control': { value: 'no-store' }
          }
        };
      }

      return request;
    }
  CODE
}
