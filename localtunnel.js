const {spawn} = require('child_process');
const path = require('path');

const args = require('minimist')(process.argv.slice(2));
const lt_path = path.join(__dirname, "node_modules/.bin/lt");
const app = spawn('node', ['--experimental-modules', lt_path, "--port" ,args.port, "--host", args.host], {
  detached: false,
  stdio:'pipe',
});

const timeout = setTimeout(() => {
  console.error(`Timeout: There is no response from the ${args.host}`);
  app.kill(9);
}, 5000);

app.on("exit",(code,signal)=>{
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
    "pid":app.pid,
    "url":url,
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