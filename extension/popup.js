// Query connection status from background service worker
chrome.runtime.sendMessage({ type: 'getStatus' }, (resp) => {
  const dot = document.getElementById('dot');
  const status = document.getElementById('status');
  const statusSubtitle = document.getElementById('statusSubtitle');
  const extVersion = document.getElementById('extVersion');

  if (resp && typeof resp.extensionVersion === 'string') {
    extVersion.textContent = `v${resp.extensionVersion}`;
  }

  if (chrome.runtime.lastError || !resp) {
    setState(dot, 'disconnected');
    status.textContent = '未连接 bridge server';
    statusSubtitle.textContent = '请先启动 webcli bridge serve';
    return;
  }

  if (resp.connected) {
    setState(dot, 'connected');
    status.textContent = '已连接 bridge server';
    statusSubtitle.textContent = '浏览器命令现在可以正常执行';
  } else if (resp.reconnecting) {
    setState(dot, 'connecting');
    status.textContent = '正在重连...';
    statusSubtitle.textContent = '正在尝试连接本地 bridge server';
  } else {
    setState(dot, 'disconnected');
    status.textContent = '未连接 bridge server';
    statusSubtitle.textContent = '请先启动 webcli bridge serve';
  }
});

function setState(dot, state) {
  dot.classList.remove('connected', 'disconnected', 'connecting');
  dot.classList.add(state);
}
