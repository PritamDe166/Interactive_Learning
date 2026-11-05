/* Cognito authorization-code flow for the static website. */
const COGNITO_DOMAIN = 'https://ap-south-2kb5kpaQta.auth.ap-south-2.amazoncognito.com';
const COGNITO_CLIENT_ID = '322ksn2mncfa1kcj8hhlhh9i5';
const AUTH_API_URL = 'https://jyibhpqcx0.execute-api.ap-south-2.amazonaws.com';
const AUTH_REDIRECT_URI = `${window.location.origin}/auth/callback.html`;

const base64Url = bytes => btoa(String.fromCharCode(...bytes))
  .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

const randomString = length => {
  const bytes = new Uint8Array(length);
  crypto.getRandomValues(bytes);
  return base64Url(bytes);
};

async function startGoogleSignIn() {
  const verifier = randomString(48);
  const state = randomString(24);
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier));

  sessionStorage.setItem('cognito_pkce_verifier', verifier);
  sessionStorage.setItem('cognito_oauth_state', state);

  const params = new URLSearchParams({
    identity_provider: 'Google',
    response_type: 'code',
    client_id: COGNITO_CLIENT_ID,
    redirect_uri: AUTH_REDIRECT_URI,
    scope: 'openid email profile',
    state,
    code_challenge_method: 'S256',
    code_challenge: base64Url(new Uint8Array(digest))
  });

  window.location.assign(`${COGNITO_DOMAIN}/oauth2/authorize?${params}`);
}

async function completeGoogleSignIn() {
  const params = new URLSearchParams(window.location.search);
  const message = document.getElementById('callbackMessage');
  const code = params.get('code');
  const error = params.get('error');
  const expectedState = sessionStorage.getItem('cognito_oauth_state');
  const verifier = sessionStorage.getItem('cognito_pkce_verifier');

  if (error) throw new Error(params.get('error_description') || error);
  if (!code) throw new Error('No authorization code was returned. Start again from the login page.');
  if (!expectedState || params.get('state') !== expectedState) throw new Error('The sign-in state did not match. Start again from the login page.');

  const response = await fetch(`${AUTH_API_URL}/session`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({code, codeVerifier: verifier})
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Authentication service rejected the session.');

  Object.entries(result.cookies || {}).forEach(([name, value]) => {
    document.cookie = `${name}=${value}; Max-Age=3600; Path=/; Secure; SameSite=Lax`;
  });
  sessionStorage.removeItem('cognito_oauth_state');
  sessionStorage.removeItem('cognito_pkce_verifier');
  window.history.replaceState({}, document.title, window.location.pathname);
  message.textContent = 'You are signed in. Your Cognito session is ready.';
  document.querySelector('.google-button').textContent = 'Continue to explainers';
  document.querySelector('.google-button').href = '../index.html';
}

window.auth = {startGoogleSignIn, completeGoogleSignIn};
