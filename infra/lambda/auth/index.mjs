import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';
import crypto from 'node:crypto';

const config = {
  cognitoDomain: process.env.COGNITO_DOMAIN,
  clientId: process.env.COGNITO_CLIENT_ID,
  redirectUri: process.env.REDIRECT_URI,
  secretArn: process.env.SECRET_ARN,
  cloudFrontDomain: process.env.CLOUDFRONT_DOMAIN,
  publicKeyId: process.env.CLOUDFRONT_PUBLIC_KEY_ID
};

const secrets = new SecretsManagerClient({});
let privateKey;

const corsHeaders = {
  'Access-Control-Allow-Origin': config.cloudFrontDomain ? `https://${config.cloudFrontDomain}` : '',
  'Access-Control-Allow-Credentials': 'true',
  'Content-Type': 'application/json'
};

const response = (statusCode, body) => ({
  statusCode,
  headers: corsHeaders,
  body: JSON.stringify(body)
});

const cloudFrontBase64 = value => Buffer.from(value).toString('base64')
  .replace(/\+/g, '-').replace(/=/g, '~').replace(/\//g, '_');

async function getPrivateKey() {
  if (privateKey) return privateKey;
  const result = await secrets.send(new GetSecretValueCommand({ SecretId: config.secretArn }));
  privateKey = result.SecretString;
  return privateKey;
}

function signedCookies() {
  const expires = Math.floor(Date.now() / 1000) + 60 * 60;
  const policy = JSON.stringify({
    Statement: [{
      Resource: `https://${config.cloudFrontDomain}/*`,
      Condition: { DateLessThan: { 'AWS:EpochTime': expires } }
    }]
  });
  const signature = crypto.createSign('RSA-SHA256').update(policy).sign(getPrivateKeySync());
  return {
    'CloudFront-Policy': cloudFrontBase64(policy),
    'CloudFront-Signature': cloudFrontBase64(signature),
    'CloudFront-Key-Pair-Id': config.publicKeyId
  };
}

let privateKeyValue;
function getPrivateKeySync() {
  return privateKeyValue;
}

async function handler(event) {
  if (event.requestContext?.http?.method === 'OPTIONS') return response(204, {});
  try {
    const body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body || {};
    if (!body.code || !body.codeVerifier) return response(400, { error: 'code and codeVerifier are required' });

    const tokenBody = new URLSearchParams({
      grant_type: 'authorization_code',
      client_id: config.clientId,
      code: body.code,
      redirect_uri: config.redirectUri,
      code_verifier: body.codeVerifier
    });
    const tokenResult = await fetch(`${config.cognitoDomain}/oauth2/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: tokenBody
    });
    const tokens = await tokenResult.json();
    if (!tokenResult.ok || !tokens.access_token) return response(401, { error: 'Cognito token exchange failed' });

    const userResult = await fetch(`${config.cognitoDomain}/oauth2/userInfo`, {
      headers: { Authorization: `Bearer ${tokens.access_token}` }
    });
    if (!userResult.ok) return response(401, { error: 'Cognito user validation failed' });

    if (!privateKeyValue) privateKeyValue = await getPrivateKey();
    return response(200, { cookies: signedCookies() });
  } catch (error) {
    console.error(error);
    return response(500, { error: 'Authentication service error' });
  }
}

export { handler };
