# Headless check of the page logic. Serves the folder, drives it with Playwright (Chromium), and asserts:
# place kept on speed change, parts start together, pitch kept for pre-rendered files, pitch drops for plain slow-down, loop wraps.
import subprocess, time, sys, asyncio, os, json
from playwright.async_api import async_playwright
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
srv=subprocess.Popen([sys.executable,'-m','http.server','8765','--directory',root],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1)
res=[]
def chk(name,ok,info=''): res.append(ok); print(('PASS ' if ok else 'FAIL ')+name+(' '+str(info) if info!='' else ''))

async def midnote_cents(pg,n=6):
    out=[]
    for _ in range(40):
        r=await pg.evaluate('__demo.measure()')
        frac=(r['musical']/0.6)%1
        if r['hz'] and 0.35<frac<0.8: out.append(r['cents'])
        if len(out)>=n: break
        await pg.wait_for_timeout(90)
    return sorted(out)[len(out)//2] if out else None

async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg=await b.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto('http://localhost:8765/index.html')
        await pg.click('#play'); await pg.wait_for_timeout(1800)
        m=await pg.evaluate('__demo.measure()')
        chk('plays at 100%',m['playing'] and m['musical']>1.0,round(m['musical'],2))
        chk('four parts start at the same instant',len(set(m['startTimes']))==1 and len(m['startTimes'])==4)
        before=await pg.evaluate('__demo.measure()')
        await pg.click('input[name=speed][value="0.8"]'); await pg.wait_for_timeout(700)
        after=await pg.evaluate('__demo.measure()')
        d=after['musical']-before['musical']
        chk('place kept when switching 100% to 80% (moves forward, no jump back or skip)',0.3<d<1.8,f"before {before['musical']:.2f} after {after['musical']:.2f}")
        await pg.wait_for_timeout(600)
        med=await midnote_cents(pg)
        chk('pre-rendered 80% keeps the pitch (within 40 cents)',med is not None and abs(med)<40,med)
        await pg.click('input[name=method][value="rate"]'); await pg.wait_for_timeout(900)
        med=await midnote_cents(pg)
        chk('plain slow-down at 80% drops the pitch (about -386 cents)',med is not None and -480<med<-300,med)
        await pg.click('input[name=method][value="pre"]'); await pg.click('input[name=speed][value="0.65"]'); await pg.wait_for_timeout(600)
        m=await pg.evaluate('__demo.measure()'); chk('65% runs',m['playing'] and m['speed']==0.65,round(m['musical'],2))
        await pg.click('#loop'); await pg.wait_for_timeout(300)
        seen=[]
        for _ in range(40):
            r=await pg.evaluate('__demo.measure()'); seen.append(r['musical']); await pg.wait_for_timeout(250)
        chk('loop keeps the place inside bars 3 and 4',all(4.7<=x<=9.7 for x in seen[2:]),f"min {min(seen[2:]):.2f} max {max(seen[2:]):.2f}")
        chk('version v10 shown in the heading and matches the code',(await pg.inner_text('#ver')).strip()=='v10' and (await pg.evaluate('window.__demo.version'))=='10')
        chk('no page errors',not errs,errs[:2])
        await b.close()
asyncio.run(main()); srv.terminate()
print('ALL PASS' if all(res) else 'SOME FAILED'); sys.exit(0 if all(res) else 1)
