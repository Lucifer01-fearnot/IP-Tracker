#!/usr/bin/env python3
"""
IPTRACER — eDEX-UI Styled IP Geolocation Tool
Run: python iptracer.py
Requires: pip install requests
"""

import http.server
import threading
import webbrowser
import urllib.request
import urllib.parse
import json
import os
import sys

PORT = 7331

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>IPTRACER</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#030712;--panel:#060d1f;--border:#0ff3;
  --cyan:#00f5ff;--cyan-dim:#00f5ff55;--cyan-glow:#00f5ff18;
  --green:#39ff14;--red:#ff2d55;--orange:#ff9500;
  --text:#a8d8e8;--text-dim:#3a6a7a;
  --font:'Share Tech Mono',monospace;--font-head:'Orbitron',monospace;
}
html,body{width:100%;height:100%;overflow:hidden;background:var(--bg);color:var(--text);font-family:var(--font);cursor:crosshair}
body::before{content:'';position:fixed;inset:0;z-index:1000;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.07) 2px,rgba(0,0,0,.07) 4px)}
body::after{content:'';position:fixed;inset:0;z-index:999;pointer-events:none;background:radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,.8) 100%)}

.app{position:fixed;inset:0;display:grid;grid-template-columns:240px 1fr 240px;grid-template-rows:50px 1fr 44px;z-index:1}
.panel{background:var(--panel);border:1px solid var(--border);position:relative;overflow:hidden}
.panel::before{content:'';position:absolute;inset:0;pointer-events:none;background:linear-gradient(135deg,var(--cyan-glow) 0%,transparent 55%)}
.panel-label{font-family:var(--font-head);font-size:7px;letter-spacing:.25em;text-transform:uppercase;color:var(--cyan);padding:7px 10px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:6px;flex-shrink:0}
.panel-label::before{content:'▸';opacity:.5}
.corner{position:absolute;width:14px;height:14px;pointer-events:none;z-index:2}
.tl{top:0;left:0;border-top:2px solid var(--cyan);border-left:2px solid var(--cyan)}
.tr{top:0;right:0;border-top:2px solid var(--cyan);border-right:2px solid var(--cyan)}
.bl{bottom:0;left:0;border-bottom:2px solid var(--cyan);border-left:2px solid var(--cyan)}
.br{bottom:0;right:0;border-bottom:2px solid var(--cyan);border-right:2px solid var(--cyan)}

/* TOPBAR */
.topbar{grid-column:1/-1;background:var(--panel);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 18px;gap:14px;box-shadow:0 0 24px rgba(0,245,255,.07)}
.logo{font-family:var(--font-head);font-size:15px;font-weight:900;color:var(--cyan);letter-spacing:.22em;text-shadow:0 0 14px var(--cyan)}
.logo span{color:var(--green)}
.sep{width:1px;height:22px;background:var(--border)}
.topinfo{font-size:9px;color:var(--text-dim);letter-spacing:.1em}
.topinfo b{color:var(--cyan)}
.ml{margin-left:auto;display:flex;gap:12px;align-items:center}
.sdot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 7px var(--green);animation:blink2 2s infinite}
@keyframes blink2{0%,100%{opacity:1}50%{opacity:.25}}
.clock{font-size:10px;color:var(--text-dim);letter-spacing:.1em}

/* BOTTOMBAR */
.bottombar{grid-column:1/-1;background:var(--panel);border-top:1px solid var(--border);display:flex;align-items:center;padding:0 16px;gap:18px;font-size:9px;color:var(--text-dim)}
.bottombar b{color:var(--cyan)}
.pbar-wrap{flex:1;height:3px;background:rgba(0,245,255,.08);border-radius:2px;overflow:hidden}
.pbar{height:100%;background:var(--cyan);width:0%;transition:width .25s;box-shadow:0 0 6px var(--cyan)}

/* LEFT */
.left{display:flex;flex-direction:column}
.input-zone{padding:14px 13px;border-bottom:1px solid var(--border)}
.ilabel{font-size:8px;letter-spacing:.2em;text-transform:uppercase;color:var(--cyan);margin-bottom:7px;display:block}
.ifield{width:100%;background:rgba(0,245,255,.04);border:1px solid var(--cyan-dim);padding:9px 11px;font-family:var(--font);font-size:13px;color:var(--cyan);outline:none;letter-spacing:.08em;transition:all .2s;caret-color:var(--green)}
.ifield:focus{border-color:var(--cyan);box-shadow:0 0 12px var(--cyan-dim),inset 0 0 8px rgba(0,245,255,.04)}
.ifield::placeholder{color:var(--text-dim)}
.tbtn{width:100%;margin-top:8px;background:transparent;border:1px solid var(--cyan);color:var(--cyan);font-family:var(--font-head);font-size:10px;letter-spacing:.2em;text-transform:uppercase;padding:9px;cursor:pointer;transition:all .2s;text-shadow:0 0 8px var(--cyan)}
.tbtn:hover{background:rgba(0,245,255,.07);box-shadow:0 0 16px var(--cyan-dim)}
.tbtn:disabled{opacity:.3;cursor:not-allowed}
.mybtn{width:100%;margin-top:5px;background:transparent;border:1px solid var(--text-dim);color:var(--text-dim);font-family:var(--font-head);font-size:9px;letter-spacing:.15em;text-transform:uppercase;padding:7px;cursor:pointer;transition:all .2s}
.mybtn:hover{border-color:var(--green);color:var(--green)}
.result-zone{padding:12px;flex:1;overflow-y:auto}
.rf{margin-bottom:10px}
.rl{font-size:7px;letter-spacing:.2em;text-transform:uppercase;color:var(--text-dim);margin-bottom:2px}
.rv{font-size:12px;color:var(--cyan);word-break:break-all;text-shadow:0 0 6px var(--cyan-dim)}
.rv.g{color:var(--green);text-shadow:0 0 6px rgba(57,255,20,.3)}
.rv.r{color:var(--red)}
.rv.o{color:var(--orange)}
.rv.big{font-size:15px;font-family:var(--font-head);letter-spacing:.05em}
.rph{font-size:10px;color:var(--text-dim);font-style:italic;padding:6px 0;letter-spacing:.04em}

/* MAP */
.map-panel{position:relative;overflow:hidden;background:#020810}
#globe-svg{width:100%;height:100%}

/* RIGHT */
.right{display:flex;flex-direction:column}
.log{padding:10px 12px;font-size:9px;line-height:1.85;overflow-y:auto;flex:1}
.ll{color:var(--text-dim);animation:fi .25s ease both}
.ll.c{color:var(--cyan)}
.ll.g{color:var(--green)}
.ll.r{color:var(--red)}
.ll.o{color:var(--orange)}
@keyframes fi{from{opacity:0;transform:translateX(4px)}to{opacity:1;transform:none}}

/* DIALOG */
.overlay{position:fixed;inset:0;z-index:500;background:rgba(0,0,0,.78);display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px)}
.dbox{background:var(--panel);border:1px solid var(--cyan);width:480px;box-shadow:0 0 50px rgba(0,245,255,.18),inset 0 0 50px rgba(0,245,255,.02);position:relative;animation:din .3s ease both}
@keyframes din{from{opacity:0;transform:scale(.93) translateY(-10px)}to{opacity:1;transform:none}}
.dhead{background:rgba(0,245,255,.05);border-bottom:1px solid var(--border);padding:13px 16px;display:flex;align-items:center;gap:10px}
.dtitle{font-family:var(--font-head);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--cyan);text-shadow:0 0 8px var(--cyan)}
.dbody{padding:24px 20px}
.ddesc{font-size:10px;color:var(--text-dim);line-height:1.8;margin-bottom:18px;letter-spacing:.04em}
.ddesc b{color:var(--cyan)}
.difield{width:100%;background:rgba(0,245,255,.04);border:1px solid var(--cyan-dim);padding:13px 14px;font-family:var(--font);font-size:15px;color:var(--cyan);outline:none;letter-spacing:.12em;transition:all .2s;caret-color:var(--green);margin-bottom:6px}
.difield:focus{border-color:var(--cyan);box-shadow:0 0 18px var(--cyan-dim)}
.difield::placeholder{color:var(--text-dim);font-size:12px}
.derr{font-size:9px;color:var(--red);min-height:16px;margin-bottom:10px;letter-spacing:.05em}
.dbtns{display:flex;gap:8px}
.dbtn{flex:1;background:transparent;border:1px solid;padding:11px;font-family:var(--font-head);font-size:9px;letter-spacing:.18em;text-transform:uppercase;cursor:pointer;transition:all .2s}
.dbtn-p{border-color:var(--cyan);color:var(--cyan);text-shadow:0 0 6px var(--cyan)}
.dbtn-p:hover{background:rgba(0,245,255,.07);box-shadow:0 0 14px var(--cyan-dim)}
.dbtn-s{border-color:var(--text-dim);color:var(--text-dim)}
.dbtn-s:hover{border-color:var(--green);color:var(--green)}
.dfoot{border-top:1px solid var(--border);padding:8px 16px;font-size:8px;color:var(--text-dim);letter-spacing:.1em;display:flex;justify-content:space-between}
.blink{animation:blinkC .8s infinite}
@keyframes blinkC{0%,100%{opacity:1}50%{opacity:0}}
</style>
</head>
<body>

<div class="overlay" id="dialog">
  <div class="dbox">
    <div class="corner tl"></div><div class="corner tr"></div>
    <div class="corner bl"></div><div class="corner br"></div>
    <div class="dhead">
      <div style="width:8px;height:8px;border-radius:50%;background:var(--cyan);box-shadow:0 0 8px var(--cyan);animation:blink2 2s infinite"></div>
      <div class="dtitle">IPTRACER // SYSTEM READY</div>
    </div>
    <div class="dbody">
      <p class="ddesc">
        Enter a target <b>IPv4</b> or <b>IPv6</b> address to begin geolocation sequence.<br>
        Globe will spin and lock onto confirmed coordinates.<br>
        <b>VPN / PROXY / DATACENTER</b> detection active.
      </p>
      <input class="difield" id="d-ip" type="text" placeholder="e.g.  49.205.123.45" maxlength="45"
        onkeydown="if(event.key==='Enter')startTrace()"/>
      <div id="d-err" class="derr"></div>
      <div class="dbtns">
        <button class="dbtn dbtn-p" onclick="startTrace()">▶ INITIATE TRACE</button>
        <button class="dbtn dbtn-s" onclick="useMyIP()">◉ MY IP</button>
      </div>
    </div>
    <div class="dfoot">
      <span>SYS:READY</span><span>SERVER:LOCALHOST</span><span>API:IP-API.COM</span>
    </div>
  </div>
</div>

<div class="app">
  <div class="topbar">
    <div class="logo">IP<span>TRACER</span></div>
    <div class="sep"></div>
    <div class="topinfo">STATUS: <b id="st">AWAITING INPUT</b></div>
    <div class="sep"></div>
    <div class="topinfo">TARGET: <b id="ti">—</b></div>
    <div class="ml">
      <div class="sdot" id="sdot"></div>
      <div class="clock" id="clk">00:00:00</div>
    </div>
  </div>

  <div class="left panel">
    <div class="corner tl"></div><div class="corner br"></div>
    <div class="panel-label">TRACE INPUT</div>
    <div class="input-zone">
      <span class="ilabel">Target IP Address</span>
      <input class="ifield" id="main-ip" type="text" placeholder="0.0.0.0" maxlength="45"
        onkeydown="if(event.key==='Enter')reTrace()"/>
      <button class="tbtn" id="tbtn" onclick="reTrace()">▶ TRACE</button>
      <button class="mybtn" onclick="useMyIPMain()">◉ USE MY IP</button>
    </div>
    <div class="result-zone" id="rzone">
      <p class="rph">// Awaiting target IP...</p>
    </div>
  </div>

  <div class="map-panel panel">
    <svg id="globe-svg"></svg>
  </div>

  <div class="right panel">
    <div class="corner tr"></div><div class="corner bl"></div>
    <div class="panel-label">TRACE LOG</div>
    <div class="log" id="log">
      <div class="ll">[SYS] IPTRACER v2.4.1 initialized</div>
      <div class="ll">[SYS] Local proxy server active</div>
      <div class="ll">[SYS] VPN detection module loaded</div>
      <div class="ll c">[SYS] Awaiting target...</div>
    </div>
  </div>

  <div class="bottombar">
    <span>QUERIES: <b id="qc">0</b></span>
    <span>LAT: <b id="blat">—</b></span>
    <span>LON: <b id="blon">—</b></span>
    <div class="pbar-wrap"><div class="pbar" id="pbar"></div></div>
    <span id="bst">IDLE</span>
  </div>
</div>

<script>
// CLOCK
function tick(){const n=new Date();document.getElementById('clk').textContent=[n.getHours(),n.getMinutes(),n.getSeconds()].map(x=>String(x).padStart(2,'0')).join(':')}
setInterval(tick,1000);tick()

// GLOBE
const svg=d3.select('#globe-svg')
const mp=document.querySelector('.map-panel')
let W,H,proj,pathFn,gG,grG,rot=[0,0,0],af,marker=null

function initGlobe(){
  W=mp.clientWidth;H=mp.clientHeight
  svg.selectAll('*').remove()
  proj=d3.geoOrthographic().scale(Math.min(W,H)*.43).translate([W/2,H/2]).clipAngle(90).rotate(rot)
  pathFn=d3.geoPath().projection(proj)
  const defs=svg.append('defs')
  const fl=defs.append('filter').attr('id','gl')
  fl.append('feGaussianBlur').attr('stdDeviation','3').attr('result','cb')
  const fm=fl.append('feMerge')
  fm.append('feMergeNode').attr('in','cb')
  fm.append('feMergeNode').attr('in','SourceGraphic')
  svg.append('circle').attr('cx',W/2).attr('cy',H/2).attr('r',proj.scale()).attr('fill','#020d1f').attr('stroke','rgba(0,245,255,0.15)').attr('stroke-width',1)
  grG=svg.append('g')
  gG=svg.append('g')
  svg.append('g').attr('id','mg')
  d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json').then(w=>{
    const countries=topojson.feature(w,w.objects.countries)
    const borders=topojson.mesh(w,w.objects.countries,(a,b)=>a!==b)
    grG.append('path').datum(d3.geoGraticule()()).attr('d',pathFn).attr('fill','none').attr('stroke','rgba(0,245,255,0.05)').attr('stroke-width',.5)
    gG.selectAll('path').data(countries.features).join('path').attr('class','ctry').attr('d',pathFn)
      .attr('fill','#09182e').attr('stroke','rgba(0,245,255,0.2)').attr('stroke-width',.5)
      .on('mouseover',function(){d3.select(this).attr('fill','#0f2545')})
      .on('mouseout',function(){d3.select(this).attr('fill','#09182e')})
    gG.append('path').datum(borders).attr('d',pathFn).attr('fill','none').attr('stroke','rgba(0,245,255,0.22)').attr('stroke-width',.4)
    idleSpin()
    if(marker)placePin(marker.lon,marker.lat,marker.label)
  }).catch(e=>{ svg.append('text').attr('x',W/2).attr('y',H/2).attr('text-anchor','middle').attr('fill','#00f5ff44').attr('font-family','Share Tech Mono,monospace').attr('font-size',11).text('[MAP LOAD ERROR]') })
}

function updPaths(){
  proj.rotate(rot);pathFn=d3.geoPath().projection(proj)
  gG.selectAll('path').attr('d',pathFn)
  grG.selectAll('path').attr('d',pathFn)
  svg.select('circle').attr('cx',proj.translate()[0]).attr('cy',proj.translate()[1]).attr('r',proj.scale())
  if(marker)refreshPin(marker.lon,marker.lat,marker.label)
}

function idleSpin(){
  let sp=0.18
  function fr(){rot[0]+=sp;updPaths();af=requestAnimationFrame(fr)}
  cancelAnimationFrame(af);requestAnimationFrame(fr)
}

function spinTo(lon,lat,done){
  cancelAnimationFrame(af)
  const tLon=-lon,tLat=-lat,sLon=rot[0],sLat=rot[1]
  const DUR=3000,ACC=0.18,DEC=0.55
  let t0=null
  function ease(t){return t<.5?4*t*t*t:(t-1)*(2*t-2)*(2*t-2)+1}
  function fr(ts){
    if(!t0)t0=ts
    let p=Math.min((ts-t0)/DUR,1)
    let spd
    if(p<ACC)spd=ease(p/ACC)
    else if(p<DEC)spd=1
    else spd=ease(1-(p-DEC)/(1-DEC))
    rot[0]=sLon+(tLon-sLon)*ease(p)+(1-p)*8*spd
    rot[1]=sLat+(tLat-sLat)*ease(p)
    updPaths();setPbar(p*100)
    if(p<1)af=requestAnimationFrame(fr)
    else{rot[0]=tLon;rot[1]=tLat;updPaths();setPbar(100);if(done)done()}
  }
  requestAnimationFrame(fr)
}

function visible(lon,lat){
  const r=proj.rotate()
  return Math.sin(lat*Math.PI/180)*Math.sin(-r[1]*Math.PI/180)+
    Math.cos(lat*Math.PI/180)*Math.cos(-r[1]*Math.PI/180)*Math.cos((lon+r[0])*Math.PI/180)>0
}

function placePin(lon,lat,label){
  marker={lon,lat,label}
  const mg=svg.select('#mg');mg.selectAll('*').remove()
  if(!visible(lon,lat))return
  const [px,py]=proj([lon,lat])
  for(let i=0;i<3;i++){
    mg.append('circle').attr('cx',px).attr('cy',py).attr('r',0).attr('fill','none')
      .attr('stroke','#00f5ff').attr('stroke-width',1.2).attr('opacity',0)
      .transition().delay(i*450).duration(1600).ease(d3.easeLinear).attr('r',20+i*12).attr('opacity',0)
      .on('end',function rep(){d3.select(this).attr('r',0).attr('opacity',.85).transition().duration(1600).ease(d3.easeLinear).attr('r',20+i*12).attr('opacity',0).on('end',rep)})
  }
  mg.append('circle').attr('cx',px).attr('cy',py).attr('r',6).attr('fill','#00f5ff').attr('stroke','#fff').attr('stroke-width',1.2).style('filter','url(#gl)')
  const lw=label.length*7+20
  mg.append('rect').attr('x',px-lw/2).attr('y',py-40).attr('width',lw).attr('height',20).attr('fill','rgba(3,7,18,.92)').attr('stroke','#00f5ff').attr('stroke-width',.8)
  mg.append('text').attr('x',px).attr('y',py-26).attr('text-anchor','middle').attr('font-family','Orbitron,monospace').attr('font-size',9).attr('fill','#00f5ff').attr('letter-spacing',1).text(label.toUpperCase())
  mg.append('line').attr('x1',px).attr('y1',py-6).attr('x2',px).attr('y2',py-21).attr('stroke','#00f5ff44').attr('stroke-width',1)
}

function refreshPin(lon,lat,label){
  if(!visible(lon,lat)){svg.select('#mg').selectAll('*').remove();return}
  const mg=svg.select('#mg')
  if(!mg.selectAll('circle').nodes().length)placePin(lon,lat,label)
}

window.addEventListener('resize',initGlobe)
initGlobe()

// PROGRESS
function setPbar(v){document.getElementById('pbar').style.width=v+'%'}

// LOG
let qc=0
function log(msg,cls=''){
  const l=document.getElementById('log')
  const d=document.createElement('div');d.className='ll'+(cls?' '+cls:'');d.textContent=msg
  l.appendChild(d);l.scrollTop=l.scrollHeight
}

// DIALOG
window.addEventListener('load',()=>setTimeout(()=>document.getElementById('d-ip').focus(),400))

async function useMyIP(){
  document.getElementById('d-ip').value='fetching...'
  try{
    const r=await fetch('/api/myip');const d=await r.json()
    document.getElementById('d-ip').value=d.ip||''
    document.getElementById('d-ip').focus()
  }catch{document.getElementById('d-err').textContent='Could not fetch your IP.'}
}
async function useMyIPMain(){
  try{
    const r=await fetch('/api/myip');const d=await r.json()
    document.getElementById('main-ip').value=d.ip||''
  }catch{}
}

function validateIP(ip){return /^(\d{1,3}\.){3}\d{1,3}$/.test(ip)||/^[0-9a-fA-F:]+$/.test(ip)}

async function startTrace(){
  const ip=document.getElementById('d-ip').value.trim()
  if(!ip){document.getElementById('d-err').textContent='// ERROR: Enter an IP address.';return}
  if(!validateIP(ip)){document.getElementById('d-err').textContent='// ERROR: Invalid IP format.';return}
  document.getElementById('dialog').style.display='none'
  await doTrace(ip)
}

async function reTrace(){
  const ip=document.getElementById('main-ip').value.trim()
  if(!ip)return;await doTrace(ip)
}

async function doTrace(ip){
  qc++;document.getElementById('qc').textContent=qc
  document.getElementById('ti').textContent=ip
  document.getElementById('st').textContent='TRACING...'
  document.getElementById('tbtn').disabled=true
  document.getElementById('bst').textContent='TRACE IN PROGRESS'
  document.getElementById('main-ip').value=ip
  setPbar(0)
  log(`[TRC] ─────────────────────────────`,'c')
  log(`[TRC] Target: ${ip}`)
  log(`[TRC] Querying geolocation...`)
  let prog=0
  const pi=setInterval(()=>{prog=Math.min(prog+3,55);setPbar(prog)},80)
  let data
  try{
    const r=await fetch(`/api/trace?ip=${encodeURIComponent(ip)}`)
    data=await r.json()
  }catch(e){
    clearInterval(pi);log(`[ERR] Request failed: ${e.message}`,'r')
    document.getElementById('st').textContent='ERROR'
    document.getElementById('tbtn').disabled=false
    document.getElementById('bst').textContent='FAILED'
    return
  }
  clearInterval(pi);setPbar(60)
  if(data.status!=='success'){
    log(`[ERR] ${data.message||'Lookup failed'}`,'r')
    document.getElementById('st').textContent='FAILED'
    document.getElementById('tbtn').disabled=false
    renderResult(null,ip);return
  }
  log(`[GEO] Country: ${data.country}`)
  log(`[GEO] City: ${data.city}, ${data.regionName}`)
  log(`[GEO] ISP: ${data.isp}`)
  log(`[GEO] Coords: ${data.lat.toFixed(4)}, ${data.lon.toFixed(4)}`)
  if(data.proxy)log(`[VPN] ⚠ PROXY / VPN DETECTED`,'o')
  if(data.hosting)log(`[VPN] ⚠ DATACENTER / HOSTING IP`,'o')
  if(!data.proxy&&!data.hosting)log(`[VPN] ✓ Clean IP — no VPN detected`,'g')
  if(data.mobile)log(`[NET] Mobile carrier network`,'c')
  const label=`${data.city}, ${data.country}`
  document.getElementById('st').textContent='SPINNING...'
  log(`[MAP] Rotating globe to target...`)
  spinTo(data.lon,data.lat,()=>{
    placePin(data.lon,data.lat,label)
    log(`[MAP] ✓ LOCKED: ${label}`,'g')
    document.getElementById('st').textContent='LOCKED ✓'
    document.getElementById('blat').textContent=data.lat.toFixed(4)
    document.getElementById('blon').textContent=data.lon.toFixed(4)
    document.getElementById('bst').textContent='TARGET LOCATED'
    document.getElementById('tbtn').disabled=false
    renderResult(data,ip)
    setTimeout(()=>{
      let sp=0.07
      function sf(){rot[0]+=sp;updPaths();if(marker)refreshPin(marker.lon,marker.lat,marker.label);af=requestAnimationFrame(sf)}
      requestAnimationFrame(sf)
    },3500)
  })
}

function renderResult(data,ip){
  const z=document.getElementById('rzone')
  if(!data){z.innerHTML='<p class="rph">// Trace failed.</p>';return}
  const vc=data.proxy||data.hosting?'o':'g'
  const vt=data.proxy?'⚠ VPN / PROXY':data.hosting?'⚠ DATACENTER':'✓ CLEAN'
  z.innerHTML=`
    <div class="rf"><div class="rl">IP Address</div><div class="rv">${data.query}</div></div>
    <div class="rf"><div class="rl">Location</div><div class="rv big">${data.city}, ${data.country}</div></div>
    <div class="rf"><div class="rl">Region</div><div class="rv">${data.regionName}</div></div>
    <div class="rf"><div class="rl">Country Code</div><div class="rv">${data.countryCode}</div></div>
    <div class="rf"><div class="rl">ZIP / Postal</div><div class="rv">${data.zip||'—'}</div></div>
    <div class="rf"><div class="rl">Coordinates</div><div class="rv">${data.lat.toFixed(5)}, ${data.lon.toFixed(5)}</div></div>
    <div class="rf"><div class="rl">Timezone</div><div class="rv">${data.timezone}</div></div>
    <div class="rf"><div class="rl">ISP</div><div class="rv">${data.isp}</div></div>
    <div class="rf"><div class="rl">Organization</div><div class="rv">${data.org}</div></div>
    <div class="rf"><div class="rl">AS Number</div><div class="rv" style="font-size:10px">${data.as}</div></div>
    <div class="rf"><div class="rl">VPN / Proxy</div><div class="rv ${vc}">${vt}</div></div>
    <div class="rf"><div class="rl">Mobile Network</div><div class="rv">${data.mobile?'YES':'NO'}</div></div>
  `
}
</script>
</body>
</html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress access logs

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == '/':
            self._html(HTML)

        elif path == '/api/trace':
            ip = params.get('ip', [''])[0].strip()
            if not ip:
                self._json({'status': 'fail', 'message': 'No IP provided'})
                return
            try:
                url = f'http://ip-api.com/json/{urllib.parse.quote(ip)}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,proxy,hosting,mobile,query'
                req = urllib.request.Request(url, headers={'User-Agent': 'IPTracer/1.0'})
                with urllib.request.urlopen(req, timeout=8) as r:
                    data = r.read().decode('utf-8')
                self._json(json.loads(data))
            except Exception as e:
                self._json({'status': 'fail', 'message': str(e)})

        elif path == '/api/myip':
            try:
                req = urllib.request.Request('https://api.ipify.org?format=json', headers={'User-Agent': 'IPTracer/1.0'})
                with urllib.request.urlopen(req, timeout=5) as r:
                    data = r.read().decode('utf-8')
                self._json(json.loads(data))
            except Exception as e:
                self._json({'error': str(e)})

        else:
            self.send_response(404)
            self.end_headers()

    def _html(self, content):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(content.encode('utf-8')))
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def _json(self, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)


def main():
    server = http.server.HTTPServer(('127.0.0.1', PORT), Handler)
    print(f'''
  ██╗██████╗ ████████╗██████╗  █████╗  ██████╗███████╗██████╗ 
  ██║██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗
  ██║██████╔╝   ██║   ██████╔╝███████║██║     █████╗  ██████╔╝
  ██║██╔═══╝    ██║   ██╔══██╗██╔══██║██║     ██╔══╝  ██╔══██╗
  ██║██║        ██║   ██║  ██║██║  ██║╚██████╗███████╗██║  ██║
  ╚═╝╚═╝        ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚═╝  ╚═╝

  Server running at http://127.0.0.1:{PORT}
  Opening browser...
  Press Ctrl+C to stop.
    ''')
    # Open browser after short delay
    threading.Timer(0.8, lambda: webbrowser.open(f'http://127.0.0.1:{PORT}')).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  [SYS] IPTRACER shutdown.')
        server.shutdown()


if __name__ == '__main__':
    main()
