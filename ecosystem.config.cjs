// PM2 ecosystem 配置 — PROD 环境
// 进程名 ocr-server / 端口由 .env 中 PORT=8004 决定

module.exports = {
  apps: [
    {
      name: "ocr-server",
      cwd: __dirname,
      script: "main.py",
      interpreter: `${__dirname}/venv/bin/python`,

      // PROD 自动拉起
      autorestart: true,
      max_memory_restart: "4G",

      // 优雅停机给 uvicorn worker 时间退出
      kill_timeout: 10000,

      // PM2 日志(只记 stdout/stderr,业务日志走 logs/ocrmac_api.log 等)
      out_file: `${__dirname}/logs/pm2-out.log`,
      error_file: `${__dirname}/logs/pm2-error.log`,
      merge_logs: true,
      time: true,

      env: {
        // 防御 PM2 client/daemon env 中可能残留的临时 TMPDIR(如 MCP 工具的 .ctx-mode-XXX)
        // 一旦原临时目录被清理,fork 出来的进程任何 tempfile 操作都会 ENOENT。
        TMPDIR: "/tmp",
      },
    },
  ],
};
