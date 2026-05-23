export interface WebViewState {
  url: string;
  safeMode: boolean;
}

export function createWebView(state: WebViewState) {
  return { url: state.url, safeMode: state.safeMode };
}
