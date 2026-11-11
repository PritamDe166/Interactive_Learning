locals {
  domain_name = "seehowitworks.dev"
  www_domain  = "www.${local.domain_name}"
}

# ---------- DNS: Route 53 hosted zone (Hostinger nameservers point here) ----------
resource "aws_route53_zone" "site" {
  name    = local.domain_name
  comment = "See How It Works website"
}

# ---------- TLS certificate (must be in us-east-1 for CloudFront) ----------
resource "aws_acm_certificate" "site" {
  provider                  = aws.us_east_1
  domain_name               = local.domain_name
  subject_alternative_names = [local.www_domain]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.site.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }

  zone_id         = aws_route53_zone.site.zone_id
  name            = each.value.name
  type            = each.value.type
  records         = [each.value.record]
  ttl             = 300
  allow_overwrite = true
}

resource "aws_acm_certificate_validation" "site" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.site.arn
  validation_record_fqdns = [for r in aws_route53_record.cert_validation : r.fqdn]
}

# ---------- www.seehowitworks.dev -> seehowitworks.dev (one canonical address) ----------
resource "aws_cloudfront_function" "www_redirect" {
  name    = "seehowitworks-www-redirect"
  runtime = "cloudfront-js-2.0"
  comment = "Redirect www to the root domain"
  publish = true
  code    = <<-JS
    function handler(event) {
      var req = event.request;
      var host = req.headers.host ? req.headers.host.value : "";
      if (host === "${local.www_domain}") {
        var qs = Object.keys(req.querystring).map(function (k) {
          return k + "=" + req.querystring[k].value;
        }).join("&");
        return {
          statusCode: 301,
          statusDescription: "Moved Permanently",
          headers: { location: { value: "https://${local.domain_name}" + req.uri + (qs ? "?" + qs : "") } }
        };
      }
      return req;
    }
  JS
}

# ---------- Site records: root and www point at CloudFront (IPv4 + IPv6) ----------
resource "aws_route53_record" "site" {
  for_each = {
    apex_a    = { name = local.domain_name, type = "A" }
    apex_aaaa = { name = local.domain_name, type = "AAAA" }
    www_a     = { name = local.www_domain, type = "A" }
    www_aaaa  = { name = local.www_domain, type = "AAAA" }
  }

  zone_id = aws_route53_zone.site.zone_id
  name    = each.value.name
  type    = each.value.type

  alias {
    name                   = aws_cloudfront_distribution.website.domain_name
    zone_id                = aws_cloudfront_distribution.website.hosted_zone_id
    evaluate_target_health = false
  }
}
