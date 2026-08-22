// smoke.sh fixture: prints an env var and the effective uid, then stays alive.
console.log("SMOKE_ENV=" + (process.env.SMOKE_VAR ?? "unset"));
console.log("SMOKE_UID=" + process.getuid());
console.log("ready");
setInterval(() => {}, 60_000);
