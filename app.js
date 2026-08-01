
:root{--green:#173e34;--green2:#25594a;--gold:#c7a96b;--cream:#f5f1e8;--ink:#24302c;--muted:#68746f;--white:#fff}
*{box-sizing:border-box}body{margin:0;font-family:Arial,Helvetica,sans-serif;background:var(--cream);color:var(--ink)}
button,input,select{font:inherit}.hidden{display:none!important}
.login{min-height:100vh;display:grid;place-items:center;background:linear-gradient(135deg,#102e27,#2c6253)}
.login-card{width:min(430px,92vw);background:#fff;border-radius:22px;padding:32px;box-shadow:0 24px 70px #0005;text-align:center}
.logo{max-width:190px;max-height:85px;object-fit:contain}.login-card input{width:100%;padding:13px;margin:7px 0;border:1px solid #cdd5d1;border-radius:10px}
.btn{border:0;border-radius:10px;padding:11px 16px;font-weight:700;cursor:pointer}.primary{background:var(--green);color:#fff}.secondary{background:#e8ecea;color:var(--green)}.gold{background:var(--gold);color:#173329}
.app{min-height:100vh}.topbar{height:78px;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 26px;position:sticky;top:0;z-index:5}
.topbar img{max-height:56px;max-width:150px;background:#fff;border-radius:8px;padding:5px}.layout{display:grid;grid-template-columns:240px 1fr;min-height:calc(100vh - 78px)}
.sidebar{background:#fff;padding:22px 14px;border-right:1px solid #ddd}.navbtn{width:100%;text-align:left;background:none;border:0;padding:12px;border-radius:9px;margin:3px 0;cursor:pointer;font-weight:700;color:#35433e}.navbtn.active,.navbtn:hover{background:#e9f0ed;color:var(--green)}
main{padding:28px;max-width:1300px;width:100%;margin:auto}.hero{background:linear-gradient(120deg,var(--green),var(--green2));color:#fff;border-radius:18px;padding:28px;margin-bottom:22px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px}.stat,.card{background:#fff;border:1px solid #dedbd3;border-radius:15px;padding:18px;box-shadow:0 5px 16px #0000000b}.stat b{font-size:25px;display:block;color:var(--green)}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.course-card{display:flex;flex-direction:column;min-height:260px}.course-card h3{margin:8px 0}.course-card p{color:var(--muted);line-height:1.45;flex:1}
.tag{display:inline-block;background:#e7eeeb;color:var(--green);padding:5px 9px;border-radius:99px;font-size:12px;font-weight:800}.tag.done{background:#e2f5e8;color:#176337}
.progress{height:9px;background:#e5e5e5;border-radius:99px;overflow:hidden;margin:12px 0}.progress div{height:100%;background:var(--gold)}
.course-layout{display:grid;grid-template-columns:280px 1fr;gap:18px}.module-list{background:var(--green);padding:16px;border-radius:15px;color:#fff}.module-list button{display:block;width:100%;text-align:left;border:1px solid #ffffff22;background:#ffffff0d;color:#fff;padding:11px;margin:6px 0;border-radius:9px;cursor:pointer}.module-list button.active{background:var(--gold);color:#173329}
.lesson{background:#fff;border-radius:15px;padding:22px;border:1px solid #ddd}.lesson video{width:100%;max-height:440px;background:#000;border-radius:12px}.lesson li{margin:8px 0}
.check label{display:flex;gap:9px;padding:10px;border-bottom:1px solid #eee}.quiz label{display:block;padding:10px;background:#f7f7f4;border-radius:8px;margin:7px 0}
table{width:100%;border-collapse:collapse;background:#fff}th,td{padding:12px;border-bottom:1px solid #e5e5e5;text-align:left}th{background:#edf1ef}
.cert{background:#fff;border:10px double var(--gold);padding:38px;text-align:center;max-width:900px;margin:auto}.cert h1{font-family:Georgia,serif;font-size:42px;color:var(--green)}
@media(max-width:900px){.layout{grid-template-columns:1fr}.sidebar{display:flex;overflow:auto}.navbtn{white-space:nowrap}.stats,.grid{grid-template-columns:1fr 1fr}.course-layout{grid-template-columns:1fr}}
@media(max-width:600px){.stats,.grid{grid-template-columns:1fr}.topbar{padding:0 12px}main{padding:16px}}
@media print{.topbar,.sidebar,.no-print{display:none!important}.layout{display:block}.cert{margin-top:30px}}
