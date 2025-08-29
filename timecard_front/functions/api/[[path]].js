// functions/api/[[path]].js

export async function onRequest(context) {
  // Get the backend API URL from the environment variable.
  // This is the secure and recommended way to store your API URL.
  const backendApiUrl = context.env.VITE_API_TARGET;

  if (!backendApiUrl) {
    return new Response("Backend API URL not configured.", { status: 500 });
  }

  // Get the original request's URL
  const url = new URL(context.request.url);

  // Construct the new URL for the backend API
  // It takes your backend's base URL and appends the path and query string
  // from the original request.
  // Example: /api/register?user=test -> https://your-backend.com/api/register?user=test
  const targetUrl = backendApiUrl + url.pathname + url.search;

  // Create a new request object to forward, but use the original request's
  // properties (method, headers, body).
  const newRequest = new Request(targetUrl, context.request);

  // Forward the request to your backend and return the response directly.
  return fetch(newRequest);
}
