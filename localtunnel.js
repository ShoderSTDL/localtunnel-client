const { spawn, spawnSync } = require('child_process');
const path = require('path');

const args = require('minimist')(process.argv.slice(2));
const lt_path = path.join(__dirname, "node_modules/localtunnel/bin/lt.js");

// This code is not merely for checking the version
// In the case of Colab, the initial loading can be very slow, causing timeout issues
// Therefore, a warm-up is necessary to load localtunnel beforehand
const preload = spawnSync('node', ['--experimental-modules', lt_path, "--version"]);
if (preload.error) {
  console.error(`localtunnel version check error: ${preload.error}`);
}
else if (preload.status !== 0) {
  console.error(`localtunnel failed with code ${preload.status}, message: ${preload.stderr.toString()}`);
}
else {
  console.info(`localtunnel version: ${preload.stdout.toString()}`);
}


const app = spawn('node', ['--experimental-modules', lt_path, "--port",Array.isArray(args.port) ? args.port[args.port.length-1] : args.port, "--host", args.host], {
  detached: false,
  stdio: 'pipe',
});

const timeout = setTimeout(() => {
  console.error(`Timeout: There is no response from the ${args.host}`);
  app.kill(9);
}, 5000);

app.on("exit", (code, signal) => {
  if (code === 0 || signal === 'SIGINT') {
    if (!app.killed) app.kill(signal);
    return;
  }
  console.error(`The process has exited due to an error.`);
  process.exit(1);
});

app.stdout.on('data', (data) => {
  const str = String(data).split("your url is:")
  if (str.length < 2) {
    throw `Failed to start localtunnel: ${host}`
  }

  const url = str[1].trim();
  const info = {
    "pid": app.pid,
    "url": url,
    "version" : preload.stdout.toString().trim()
  }
  console.info(JSON.stringify(info));

  clearTimeout(timeout);
  app.stdout.destroy();
  app.stderr.destroy();
  app.unref();
});

app.stderr.on('data', (data) => {
  console.error(`error: ${data}`);
  if (!app.killed) app.kill(9);
});