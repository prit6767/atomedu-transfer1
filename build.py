with open('/tmp/atom/logo-dark-sm.b64') as f: dark_b64 = f.read().strip()
with open('/tmp/atom/logo-light-sm.b64') as f: light_b64 = f.read().strip()

SEND_TO = ''

CONTROL_NOTE = r'''
<div class="control-note">
  <b>You are writing this.</b> Atom drafts. You edit or rewrite. Nothing goes out until you say yes.
</div>
'''

PAGE_HOME = r'''
<div class="ws-page on" data-page="home">
  <h1 class="ws-hello">Good to see you, <span class="it" id="hello-name">Ms. Chen</span>.</h1>
  <div class="ws-sub" id="home-sub">Everything you draft with Atom lives here.</div>

  <div id="home-awaiting"></div>

  <div id="home-recent-wrap" style="display:none;">
    <div class="grid-label">Recent</div>
    <div class="recent-list" id="home-recent"></div>
  </div>

  <div class="empty" id="home-empty" style="display:none;">
    <div class="empty-icon">&#43;</div>
    <div class="empty-title">Draft your <span class="it">first thing.</span></div>
    <div class="empty-body">Every draft you make with Atom lands here. Nothing goes out until you approve it. Start with an assignment, a quiz, a note home, or anything else in the "New draft" menu.</div>
    <button class="btn empty-cta" data-empty-cta>Draft your first thing <span class="arrow">&rarr;</span></button>
  </div>
</div>
'''

PAGE_QUEUE = r'''
<div class="ws-page" data-page="queue">
  <div class="ph"><h1>Approval <span class="it">queue</span></h1><p>Everything waiting on you. Nothing has gone out.</p></div>
  <div id="queue-list"></div>
  <div class="empty" id="queue-empty" style="display:none;">
    <div class="empty-icon">&#10003;</div>
    <div class="empty-title">All <span class="it">clear.</span></div>
    <div class="empty-body">You have no drafts awaiting your yes. Start a new one from the "+ New draft" menu.</div>
  </div>
  <div id="queue-sent-wrap" style="display:none; margin-top: 40px;">
    <div class="grid-label">Sent history</div>
    <div class="recent-list" id="queue-sent"></div>
  </div>
</div>
'''

PAGE_CLASSES = r'''
<div class="ws-page" data-page="classes">
  <div class="ph"><h1>Your <span class="it">classes</span></h1><p>Every class you teach.</p></div>
  <div class="tools">
    <div class="tool"><div class="ic">1</div><div class="tt">Period 1</div><div class="td">Morning block</div></div>
    <div class="tool"><div class="ic">2</div><div class="tt">Period 2</div><div class="td">Morning block</div></div>
    <div class="tool"><div class="ic">3</div><div class="tt">Period 3</div><div class="td">Morning block</div></div>
    <div class="tool"><div class="ic">5</div><div class="tt">Period 5</div><div class="td">Morning block</div></div>
    <div class="tool"><div class="ic">+</div><div class="tt">Add a class</div><div class="td">Start a new class.</div></div>
  </div>
</div>
'''

def maker_shell(title, italic, sub, prompt_val, dest_default, approve_label, body):
    return r'''
<div class="ws-page" data-page="__PAGE__">
  <div class="ph"><h1>__TITLE__ <span class="it">__IT__</span></h1><p>__SUB__</p></div>
  ''' + CONTROL_NOTE + r'''
  <div class="ask-box">
    <div class="ask-label">What do you want to make?</div>
    <div class="ask-input"><span class="ask-prompt">&#43;</span><input value="__PROMPT__">
      <button class="ask-go">Draft it &rarr;</button>
    </div>
  </div>
  __BODY__
  ''' + SEND_TO + r'''
  <div class="approve-bar"><button>Return to draft</button><button class="primary">__APPROVE__</button></div>
</div>
'''

PAGE_ASSIGNMENT = maker_shell('Assignment', 'maker', 'A printable worksheet. A printable worksheet ready for handout.',
  '6 question rate of change worksheet for period 3, mix MC and graph, 20 points', 'Canvas',
  'Approve', r'''
  <div class="worksheet">
    <div class="ws-title">Rate of Change</div>
    <div class="ws-meta">Name <span class="ln"></span> Date <span class="ln sm"></span> Period <span class="ln xs"></span></div>
    <hr class="ws-hr">
    <div class="ws-q">
      <div class="ws-qh"><b>1.</b> <span class="pts">(1 point)</span> <span class="qtype">Multiple choice</span></div>
      <div class="ws-qb">Which expression is the derivative of f(x) = 3x&sup2; &minus; 4x + 1?</div>
      <ol class="ws-opts"><li>6x &minus; 4</li><li>3x &minus; 4</li><li>x&sup3; &minus; 2x&sup2; + x</li><li>6x + 4</li></ol>
    </div>
    <div class="ws-q">
      <div class="ws-qh"><b>2.</b> <span class="pts">(2 points)</span> <span class="qtype">Short answer</span></div>
      <div class="ws-qb">Evaluate &int;(2x + 3) dx.</div>
      <div class="ws-lines"><div class="wl"></div><div class="wl"></div></div>
    </div>
    <div class="ws-q">
      <div class="ws-qh"><b>3.</b> <span class="pts">(4 points)</span> <span class="qtype">Graph</span></div>
      <div class="ws-qb">Sketch f(x) = x&sup2; on the axes below. Mark the point where the slope equals 4.</div>
      <div class="ws-graph"></div>
    </div>
  </div>
''').replace('__PAGE__','assignment').replace('__TITLE__','Assignment').replace('__IT__','maker').replace('__SUB__','A printable worksheet. A printable worksheet ready for handout.').replace('__PROMPT__','6 question rate of change worksheet for period 3, mix MC and graph, 20 points').replace('__APPROVE__','Approve').replace('__BODY__', r'''
  <div class="worksheet">
    <div class="ws-title">Rate of Change</div>
    <div class="ws-meta">Name <span class="ln"></span> Date <span class="ln sm"></span> Period <span class="ln xs"></span></div>
    <hr class="ws-hr">
    <div class="ws-q">
      <div class="ws-qh"><b>1.</b> <span class="pts">(1 point)</span> <span class="qtype">Multiple choice</span></div>
      <div class="ws-qb">Which expression is the derivative of f(x) = 3x&sup2; &minus; 4x + 1?</div>
      <ol class="ws-opts"><li>6x &minus; 4</li><li>3x &minus; 4</li><li>x&sup3; &minus; 2x&sup2; + x</li><li>6x + 4</li></ol>
    </div>
    <div class="ws-q">
      <div class="ws-qh"><b>2.</b> <span class="pts">(2 points)</span> <span class="qtype">Short answer</span></div>
      <div class="ws-qb">Evaluate &int;(2x + 3) dx.</div>
      <div class="ws-lines"><div class="wl"></div><div class="wl"></div></div>
    </div>
    <div class="ws-q">
      <div class="ws-qh"><b>3.</b> <span class="pts">(4 points)</span> <span class="qtype">Graph</span></div>
      <div class="ws-qb">Sketch f(x) = x&sup2; on the axes below. Mark the point where the slope equals 4.</div>
      <div class="ws-graph"></div>
    </div>
  </div>
''')

PAGE_QUIZ = r'''
<div class="ws-page" data-page="quiz">
  <div class="ph"><h1>Quiz &amp; test <span class="it">builder</span></h1><p>Mix multiple choice, short answer, and diagrams. Includes an answer key.</p></div>
  ''' + CONTROL_NOTE + r'''
  <div class="ask-box">
    <div class="ask-label">What do you want to make?</div>
    <div class="ask-input"><span class="ask-prompt">&#43;</span><input value="12 question photosynthesis quiz for period 3, mostly MC, 25 min">
      <button class="ask-go">Draft it &rarr;</button>
    </div>
  </div>
  <div class="worksheet">
    <div class="ws-title">Photosynthesis, short quiz</div>
    <div class="ws-meta">Name <span class="ln"></span> Date <span class="ln sm"></span> Period <span class="ln xs"></span></div>
    <hr class="ws-hr">
    <div class="ws-q"><div class="ws-qh"><b>1.</b> <span class="pts">(1 point)</span> <span class="qtype">Multiple choice</span></div><div class="ws-qb">Which pair does a plant take in for photosynthesis?</div><ol class="ws-opts"><li>Water and salt</li><li>Water and carbon dioxide</li><li>Oxygen and nitrogen</li><li>Sugar and oxygen</li></ol></div>
    <div class="ws-q"><div class="ws-qh"><b>2.</b> <span class="pts">(1 point)</span> <span class="qtype">Multiple choice</span></div><div class="ws-qb">Chlorophyll makes leaves look what color?</div><ol class="ws-opts"><li>Red</li><li>Green</li><li>Blue</li><li>Yellow</li></ol></div>
    <div class="ws-q"><div class="ws-qh"><b>3.</b> <span class="pts">(2 points)</span> <span class="qtype">Short answer</span></div><div class="ws-qb">Describe what happens to a plant left in a dark closet for a week.</div><div class="ws-lines"><div class="wl"></div><div class="wl"></div></div></div>
  </div>
  ''' + SEND_TO + r'''
  <div class="approve-bar"><button>Return to draft</button><button class="primary">Approve</button></div>
</div>
'''

PAGE_RUBRIC = r'''
<div class="ws-page" data-page="rubric">
  <div class="ph"><h1>Rubric <span class="it">builder</span></h1><p>Rows tied to a standard. Attach to any assignment.</p></div>
  ''' + CONTROL_NOTE + r'''
  <div class="rubric-matrix">
    <div class="rm-row rm-head"><div>Row / Standard</div><div>1 &middot; Beginning</div><div>2 &middot; Developing</div><div>3 &middot; Meeting</div><div>4 &middot; Exceeding</div></div>
    <div class="rm-row"><div><b>Claim</b><div class="mm">W.6.1a</div></div><div>No clear claim</div><div>Claim present, unclear</div><div>Clear, arguable claim</div><div>Nuanced, precise claim</div></div>
    <div class="rm-row"><div><b>Evidence</b><div class="mm">W.6.1b</div></div><div>Little or no evidence</div><div>Evidence, uneven fit</div><div>Relevant, sufficient</div><div>Layered, well chosen</div></div>
    <div class="rm-row"><div><b>Reasoning</b><div class="mm">W.6.1b</div></div><div>Restates evidence</div><div>Reasoning shows</div><div>Connects evidence to claim</div><div>Addresses counter</div></div>
    <div class="rm-row"><div><b>Conventions</b><div class="mm">L.6.1</div></div><div>Frequent errors</div><div>Errors distract</div><div>Errors do not distract</div><div>Precise, controlled</div></div>
  </div>
  <div class="approve-bar"><button>Return to draft</button><button class="primary">Approve &amp; save</button></div>
</div>
'''

PAGE_LESSON = r'''
<div class="ws-page" data-page="lesson">
  <div class="ph"><h1>Lesson <span class="it">planner</span></h1><p>One class, or a whole unit.</p></div>
  ''' + CONTROL_NOTE + r'''
  <div class="timeline">
    <div class="tl-row"><div class="tl-time">Warm up</div><div class="tl-card"><b>Silent write, 5 min</b><div class="mm">Project the question.</div></div></div>
    <div class="tl-row"><div class="tl-time">Mini lesson</div><div class="tl-card"><b>Chlorophyll and light, 12 min</b><div class="mm">Slides 3 to 9.</div></div></div>
    <div class="tl-row"><div class="tl-time">Practice</div><div class="tl-card"><b>Guided, 15 min &middot; then independent, 10 min</b><div class="mm">Handout, 2 pages.</div></div></div>
    <div class="tl-row"><div class="tl-time">Exit</div><div class="tl-card"><b>One sentence exit ticket, 3 min</b><div class="mm">What does chlorophyll do?</div></div></div>
  </div>
  <div class="approve-bar"><button>Return to draft</button><button class="primary">Approve</button></div>
</div>
'''

PAGE_PASSAGES = r'''
<div class="ws-page" data-page="passages">
  <div class="ph"><h1>Reading <span class="it">passages</span></h1><p>Leveled to your class. Questions attached.</p></div>
  ''' + CONTROL_NOTE + r'''
  <div class="ask-box">
    <div class="ask-label">What do you want to make?</div>
    <div class="ask-input"><span class="ask-prompt">&#43;</span><input value="350 word passage on how leaves turn light into food, 820L, warm and curious">
      <button class="ask-go">Draft it &rarr;</button>
    </div>
  </div>
  <div class="worksheet">
    <div class="ws-title">How leaves turn light into food</div>
    <hr class="ws-hr">
    <div class="passage">
      <p>You have walked past a tree a thousand times and never thought about what it eats. It does not eat, really. Not the way you do. A tree makes its own food, right there in its leaves, using sunlight.</p>
      <p>Inside each leaf are tiny green pockets called <b>chlorophyll</b>. When light hits the leaf, chlorophyll grabs it. The leaf pulls in water from the roots and carbon dioxide from the air. Then the leaf turns those three things into sugar. The tree uses that sugar to grow.</p>
    </div>
    <hr class="ws-hr">
    <div class="ws-q"><div class="ws-qh"><b>1.</b> <span class="pts">(2 points)</span> <span class="qtype">Short answer</span></div><div class="ws-qb">What are the three things a leaf uses to make food?</div><div class="ws-lines"><div class="wl"></div><div class="wl"></div></div></div>
  </div>
  ''' + SEND_TO + r'''
  <div class="approve-bar"><button>Return to draft</button><button class="primary">Approve</button></div>
</div>
'''

PAGE_SLIDES = r'''
<div class="ws-page" data-page="slides">
  <div class="ph"><h1>Slides &amp; <span class="it">boards</span></h1><p>Slides for the projector, notes for the board.</p></div>
  ''' + CONTROL_NOTE + r'''
  <div class="ask-box">
    <div class="ask-label">What do you want to make?</div>
    <div class="ask-input"><span class="ask-prompt">&#43;</span><input value="8 slide photosynthesis intro for period 3, warm up on slide 1, exit ticket on slide 8">
      <button class="ask-go">Draft it &rarr;</button>
    </div>
  </div>
  <div class="slides">
    <div class="slide"><div class="sn">01</div><div class="sc"><b>Photosynthesis</b><div class="mm">Warm up: what does a plant eat?</div></div></div>
    <div class="slide"><div class="sn">02</div><div class="sc"><b>Three things a leaf needs</b><div class="mm">Water, light, carbon dioxide</div></div></div>
    <div class="slide"><div class="sn">03</div><div class="sc"><b>Chlorophyll</b><div class="mm">Where it lives, what it does</div></div></div>
    <div class="slide"><div class="sn">04</div><div class="sc"><b>Diagram: inside the leaf</b><div class="mm">Label the arrows</div></div></div>
    <div class="slide"><div class="sn">05</div><div class="sc"><b>Sugar, oxygen, out</b><div class="mm">What the plant gives back</div></div></div>
    <div class="slide"><div class="sn">06</div><div class="sc"><b>Try it: partner talk</b><div class="mm">Explain in one sentence</div></div></div>
    <div class="slide"><div class="sn">07</div><div class="sc"><b>Exit ticket</b><div class="mm">One input, one output</div></div></div>
    <div class="slide"><div class="sn">+</div><div class="sc"><b>Add slide</b><div class="mm">Blank or diagram</div></div></div>
  </div>
  <div class="approve-bar"><button>Return to draft</button><button class="primary">Approve</button></div>
</div>
'''

PAGE_DOCS = r'''
<div class="ws-page" data-page="docs">
  <div class="ph"><h1>Docs &amp; <span class="it">handouts</span></h1><p>Family letters, syllabi, permission slips, newsletters.</p></div>
  ''' + CONTROL_NOTE + r'''
  <div class="ask-box">
    <div class="ask-label">What do you want to make?</div>
    <div class="ask-input"><span class="ask-prompt">&#43;</span><input value="one page unit overview for families, Unit 3 Plants, warm and plain, EN + ES">
      <button class="ask-go">Draft it &rarr;</button>
    </div>
  </div>
  <div class="worksheet">
    <div class="ws-title">A quick note from room 214</div>
    <div class="passage">
      <p>Hi families,</p>
      <p>This month, our class is studying plants. We are learning how a leaf makes food out of sunlight, water, and air, and why leaves look green. It is a hands on unit, so students will be using magnifiers, a few real leaves, and their own careful observations.</p>
      <p>Two ways you can help at home: ask your student to explain photosynthesis in one sentence at dinner, and take a walk to look at how different leaves are shaped. That is the whole homework.</p>
      <p>Warmly,<br>Ms. Chen</p>
    </div>
    <div class="chips" style="margin-top:14px;"><span class="chip on">EN</span><span class="chip">ES draft ready</span></div>
  </div>
  <div class="approve-bar"><button>Return to draft</button><button class="primary">Approve</button></div>
</div>
'''

PAGE_NOTES = r'''
<div class="ws-page" data-page="notes">
  <div class="ph"><h1>Notes <span class="it">home</span></h1><p>You write the message. Atom checks tone and drafts a translation.</p></div>
  ''' + CONTROL_NOTE + r'''
  <div class="worksheet">
    <div class="doc-tag">Your draft &middot; message home</div>
    <textarea class="msg-write">Hi Ms. Alvarez,

I wanted to reach out about Diego. He is doing thoughtful work in class this year, and I have really enjoyed his questions during our plants unit. I noticed he was a little quieter on Friday and did not turn in the lab we started last week. Nothing to worry about, I just wanted you to know.

Would it help to schedule a quick check in with Diego on Friday during lunch? I can walk him through the lab and give him a chance to finish it in a smaller setting.

Warmly,
Ms. Chen</textarea>
    <div class="chips"><span class="chip on">EN</span><span class="chip">ES draft ready</span></div>
  </div>
  <div class="approve-bar"><button>Return to draft</button><button class="primary">Approve</button></div>
</div>
'''

PAGE_DIFF = r'''
<div class="ws-page" data-page="diff">
  <div class="ph"><h1>Differentia<span class="it">tion</span></h1><p>Same assignment, adapted for reading level, IEP, or your ELL group.</p></div>
  ''' + CONTROL_NOTE + r'''
  <div class="diff-grid">
    <div class="diff-col"><div class="section-label">On grade</div><div class="worksheet mini"><p><b>3.</b> If a plant sits in a dark closet for a week, what happens? Explain in 2 sentences.</p></div></div>
    <div class="diff-col"><div class="section-label">Scaffolded</div><div class="worksheet mini"><p><b>3.</b> A plant sits in a dark closet. What happens? Choose one: (a) grows tall (b) stays green (c) fades and dies.</p></div></div>
    <div class="diff-col"><div class="section-label">ELL frames</div><div class="worksheet mini"><p><b>3.</b> In a dark closet, a plant _____ because it does not have _____.</p></div></div>
  </div>
  <div class="approve-bar"><button>Return to drafts</button><button class="primary">Approve all three</button></div>
</div>
'''

PAGE_STANDARDS = r'''
<div class="ws-page" data-page="standards">
  <div class="ph"><h1>Standards <span class="it">library</span></h1><p>What you teach against.</p></div>
  <div class="std">
    <div class="std-cat">NGSS &middot; Middle School Life Science</div>
    <div class="std-row"><b>MS-LS1-6</b><span>Construct a scientific explanation for photosynthesis.</span><span class="pill ok">In use</span></div>
    <div class="std-row"><b>MS-LS1-7</b><span>Model food, water, and energy through an ecosystem.</span><span class="pill">Not yet</span></div>
    <div class="std-cat">CCSS &middot; Writing, Grade 6</div>
    <div class="std-row"><b>W.6.1a</b><span>Introduce claims and organize the reasons.</span><span class="pill ok">In use</span></div>
    <div class="std-row"><b>W.6.1b</b><span>Support claims with clear reasons and relevant evidence.</span><span class="pill ok">In use</span></div>
    <div class="std-cat">CCSS &middot; Math, High School</div>
    <div class="std-row"><b>HSF-IF.B.6</b><span>Calculate and interpret the average rate of change.</span><span class="pill ok">In use</span></div>
  </div>
</div>
'''

PAGE_SETTINGS = r'''
<div class="ws-page" data-page="settings">
  <div class="ph"><h1>Settin<span class="it">gs</span></h1></div>
  <div class="settings">
    <div class="sblock">
      <h3>You</h3>
      <div class="frow"><label>Name</label><input value="Ms. Chen"></div>
      <div class="frow"><label>School email</label><input value="chen@rooseveltms.org"></div>
      <div class="frow"><label>Subject &amp; grade</label><input value="6th grade Science"></div>
    </div>
    <div class="sblock">
      <h3>Voice</h3>
      <p class="mm">Atom writes drafts in a voice close to yours. Paste something you already wrote.</p>
      <textarea>Warm, direct, second person. Everyday comparisons. No big words for the sake of it.</textarea>
    </div>
    <div class="sblock">
      <h3>Privacy</h3>
      <div class="toggle"><span>Never use student work to train models</span><span class="sw on">On</span></div>
      <div class="toggle"><span>Never sell your data</span><span class="sw on">On</span></div>
      <div class="toggle"><span>Delete student work after this school year</span><span class="sw on">On</span></div>
    </div>
    <div class="approve-bar"><button>Cancel</button><button class="primary">Save</button></div>
  </div>
</div>
'''

PAGES = {
    'home': PAGE_HOME,
    'queue': PAGE_QUEUE,
    'classes': PAGE_CLASSES,
    'assignment': PAGE_ASSIGNMENT,
    'quiz': PAGE_QUIZ,
    'rubric': PAGE_RUBRIC,
    'lesson': PAGE_LESSON,
    'passages': PAGE_PASSAGES,
    'slides': PAGE_SLIDES,
    'docs': PAGE_DOCS,
    'notes': PAGE_NOTES,
    'diff': PAGE_DIFF,
    'standards': PAGE_STANDARDS,
    'settings': PAGE_SETTINGS,
}

all_pages = ''.join(PAGES.values())

STYLES = r'''
<style>
  :root {
    --bg: #f4efe4; --bg-elev: #ffffff; --paper: #fbfaf5;
    --ink: #0b1226; --ink-soft: #2a324a; --muted: #5a6178;
    --line: rgba(11, 18, 38, 0.12);
    --line-strong: rgba(11, 18, 38, 0.22);
    --stamp: #b7331f; --ok: #1e7a4f;
    --logo-url: url(data:image/png;base64,__LIGHT__);
  }
  :root[data-theme="dark"] {
    --bg: #060a1a; --bg-elev: #0d1430; --paper: #10193a;
    --ink: #f4efe4; --ink-soft: #d8d2c3; --muted: #8a91a8;
    --line: rgba(244, 239, 228, 0.14);
    --line-strong: rgba(244, 239, 228, 0.28);
    --stamp: #e07b5c; --ok: #4bd47a;
    --logo-url: url(data:image/png;base64,__DARK__);
  }

  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    background: var(--bg); color: var(--ink);
    font-family: "Fraunces", "Iowan Old Style", Georgia, serif;
    -webkit-font-smoothing: antialiased; line-height: 1.55; overflow-x: hidden;
  }
  .sans { font-family: "Inter", -apple-system, "Segoe UI", Roboto, sans-serif; }
  a { color: inherit; text-decoration: none; }
  .wrap { max-width: 1080px; margin: 0 auto; padding: 0 28px; }
  #landing.hidden, #workspace.hidden { display: none; }

  /* landing */
  .nav {
    position: sticky; top: 0; z-index: 20;
    backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
    background: color-mix(in srgb, var(--bg) 78%, transparent);
    border-bottom: 1px solid var(--line);
  }
  .nav-in { display: flex; align-items: center; justify-content: space-between; height: 64px; }
  .brand { display: flex; align-items: center; gap: 10px; font-family: "Inter", sans-serif; font-weight: 700; font-size: 17px; letter-spacing: -0.01em; }
  .brand-mark { width: 28px; height: 28px; background: var(--logo-url) center / contain no-repeat; }
  .nav-right { display: flex; align-items: center; gap: 12px; }
  .theme-toggle {
    font-family: "Inter", sans-serif; font-size: 12px; padding: 6px 10px;
    border: 1px solid var(--line-strong); border-radius: 999px;
    background: transparent; color: var(--ink-soft); cursor: pointer;
    letter-spacing: 0.04em; text-transform: uppercase;
  }
  .nav-cta {
    font-family: "Inter", sans-serif; font-size: 14px; font-weight: 600;
    background: var(--ink); color: var(--bg);
    padding: 9px 16px; border-radius: 999px; border: 1px solid var(--ink); cursor: pointer;
  }
  .nav-link { font-family: "Inter", sans-serif; font-size: 13.5px; color: var(--ink-soft); background: transparent; border: none; cursor: pointer; padding: 6px 4px; }
  .nav-link:hover { color: var(--ink); }

  .hero { padding: 96px 0 72px; }
  .eyebrow { font-family: "Inter", sans-serif; font-size: 12px; text-transform: uppercase; letter-spacing: 0.18em; color: var(--muted); margin-bottom: 24px; display: inline-flex; align-items: center; gap: 10px; }
  .eyebrow .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--stamp); box-shadow: 0 0 0 4px color-mix(in srgb, var(--stamp) 20%, transparent); }
  h1.headline { font-size: clamp(48px, 8.5vw, 100px); line-height: 0.96; letter-spacing: -0.035em; font-weight: 400; margin: 0 0 24px; max-width: 14ch; }
  h1.headline .it { font-style: italic; font-weight: 300; }
  .lede { font-family: "Inter", sans-serif; font-size: 18px; color: var(--ink-soft); max-width: 48ch; margin: 0 0 36px; }
  .cta-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
  .btn {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 13px 20px; border-radius: 999px;
    font-family: "Inter", sans-serif; font-size: 15px; font-weight: 600;
    border: 1px solid var(--ink); background: var(--ink); color: var(--bg);
    transition: transform .15s ease; cursor: pointer;
  }
  .btn:hover { transform: translateY(-1px); }
  .btn.ghost { background: transparent; color: var(--ink); border: 1px solid var(--line-strong); }
  .arrow { display:inline-block; transition: transform .2s ease; }
  .btn:hover .arrow { transform: translateX(3px); }
  .fine { font-family: "Inter", sans-serif; font-size: 13px; color: var(--muted); margin-top: 18px; }

  .section { padding: 72px 0; border-top: 1px solid var(--line); }
  .section-label { font-family: "Inter", sans-serif; font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase; color: var(--muted); margin-bottom: 16px; }
  h2.big { font-size: clamp(32px, 4.6vw, 50px); line-height: 1.03; letter-spacing: -0.028em; font-weight: 400; max-width: 22ch; margin: 0; }
  h2.big .it { font-style: italic; font-weight: 300; }

  .flow { margin-top: 40px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; border: 1px solid var(--line-strong); border-radius: 18px; overflow: hidden; background: var(--bg-elev); }
  @media (max-width: 780px) { .flow { grid-template-columns: 1fr; } }
  .step { padding: 32px 28px; border-right: 1px solid var(--line); position: relative; }
  .step:last-child { border-right: none; }
  @media (max-width: 780px) { .step { border-right: none; border-bottom: 1px solid var(--line); } .step:last-child { border-bottom: none; } }
  .step-num { font-family: "Inter", sans-serif; font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase; color: var(--muted); margin-bottom: 18px; }
  .step h3 { font-size: 24px; letter-spacing: -0.02em; font-weight: 400; line-height: 1.15; margin: 0 0 10px; }
  .step h3 .it { font-style: italic; }
  .step p { font-family: "Inter", sans-serif; font-size: 14px; line-height: 1.55; color: var(--ink-soft); margin: 0; }
  .step.review { background: color-mix(in srgb, var(--stamp) 8%, var(--bg-elev)); }
  .step .stamp { position: absolute; top: 28px; right: 28px; font-family: "Inter", sans-serif; font-size: 10px; letter-spacing: 0.22em; text-transform: uppercase; color: var(--stamp); border: 1px solid var(--stamp); padding: 3px 8px; border-radius: 4px; transform: rotate(6deg); font-weight: 600; }

  .provider-row { margin-top: 30px; display: flex; gap: 10px; flex-wrap: wrap; align-items: center; padding: 22px; border: 1px solid var(--line-strong); border-radius: 16px; background: var(--bg-elev); font-family: "Inter", sans-serif; }
  .provider-row .pl { font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted); font-weight: 700; margin-right: 8px; }
  .provider-row .pchip { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; padding: 8px 12px; border-radius: 999px; border: 1px solid var(--line-strong); background: transparent; color: var(--ink); }
  .provider-row .pchip .pi { width: 18px; height: 18px; border-radius: 5px; display: inline-flex; align-items: center; justify-content: center; color: #fff; font-family: "Fraunces", Georgia, serif; font-weight: 700; font-size: 11px; }

  .tiles { margin-top: 40px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  @media (max-width: 820px) { .tiles { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 500px) { .tiles { grid-template-columns: 1fr; } }
  .tile { padding: 20px 20px; border-radius: 14px; border: 1px solid var(--line); background: var(--bg-elev); }
  .tile .tn { font-family: "Fraunces", Georgia, serif; font-size: 18px; letter-spacing: -0.015em; font-weight: 500; margin-bottom: 4px; }
  .tile .tn .it { font-style: italic; }
  .tile .tp { font-family: "Inter", sans-serif; font-size: 12.5px; color: var(--muted); line-height: 1.55; }

  .free { padding: 96px 0; text-align: center; border-top: 1px solid var(--line); }
  .free .huge { font-size: clamp(56px, 12vw, 160px); line-height: 0.9; letter-spacing: -0.05em; font-weight: 400; margin: 0; }
  .free .huge .it { font-style: italic; font-weight: 300; }
  .free .caption { font-family: "Inter", sans-serif; font-size: 15px; color: var(--ink-soft); max-width: 44ch; margin: 22px auto 0; line-height: 1.55; }

  .end { padding: 100px 0 90px; text-align: center; border-top: 1px solid var(--line); }
  .end .tag { font-size: clamp(44px, 7vw, 84px); line-height: 1; letter-spacing: -0.035em; font-weight: 400; margin: 0 0 32px; }
  .end .tag .it { font-style: italic; font-weight: 300; }

  .ft { border-top: 1px solid var(--line); background: color-mix(in srgb, var(--ink) 3%, var(--bg)); padding: 40px 0 28px; font-family: "Inter", sans-serif; color: var(--muted); font-size: 13px; }
  .ft-row { display: flex; justify-content: space-between; align-items: center; gap: 20px; flex-wrap: wrap; }
  .ft a { color: var(--muted); }
  .ft a:hover { color: var(--ink); }
  .ft-links { display: flex; gap: 20px; flex-wrap: wrap; }
  .kicker { color: var(--stamp); font-family: "Inter", sans-serif; font-size: 12px; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 600; margin-bottom: 12px; }


  /* workspace */
  .ws-shell { display: grid; grid-template-columns: 240px 1fr; min-height: 100vh; }
  @media (max-width: 900px) { .ws-shell { grid-template-columns: 1fr; } }
  .ws-side { border-right: 1px solid var(--line); padding: 22px 18px; font-family: "Inter", sans-serif; position: sticky; top: 0; align-self: start; height: 100vh; overflow-y: auto; background: var(--bg); }
  @media (max-width: 900px) { .ws-side { position: static; height: auto; border-right: none; border-bottom: 1px solid var(--line); } }
  .ws-brand { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 16px; margin-bottom: 22px; letter-spacing: -0.01em; cursor: pointer; }
  .ws-brand .brand-mark { width: 26px; height: 26px; }
  .ws-class { background: var(--bg-elev); border: 1px solid var(--line-strong); border-radius: 10px; padding: 10px 12px; margin-bottom: 22px; }
  .ws-class .cn { font-weight: 600; font-size: 13.5px; }
  .ws-class .cp { font-size: 11px; color: var(--muted); letter-spacing: 0.06em; text-transform: uppercase; margin-top: 2px; }
  .ws-nav-label { font-size: 10px; letter-spacing: 0.22em; text-transform: uppercase; color: var(--muted); margin: 14px 8px 8px; }
  .ws-nav { display: flex; flex-direction: column; gap: 2px; }
  .ws-nav a { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 8px; font-size: 13.5px; color: var(--ink-soft); cursor: pointer; }
  .ws-nav a:hover { background: color-mix(in srgb, var(--ink) 5%, transparent); color: var(--ink); }
  .ws-nav a.on { background: color-mix(in srgb, var(--ink) 8%, transparent); color: var(--ink); font-weight: 600; }
  .ws-teacher { margin-top: 24px; padding: 10px; border-radius: 10px; display: flex; align-items: center; gap: 10px; border: 1px solid var(--line); }
  .ws-teacher-info { flex: 1; min-width: 0; }
  .signout { background: transparent; border: none; color: var(--muted); cursor: pointer; padding: 6px 10px; border-radius: 6px; font-size: 14px; }
  .signout:hover { background: color-mix(in srgb, var(--stamp) 12%, transparent); color: var(--stamp); }

  /* New draft menu */
  .new-wrap { position: relative; }
  .new-menu {
    display: none;
    position: absolute; top: calc(100% + 6px); right: 0;
    min-width: 200px;
    background: var(--bg-elev); border: 1px solid var(--line-strong);
    border-radius: 12px; padding: 6px;
    box-shadow: 0 20px 40px -10px rgba(0,0,0,0.3);
    z-index: 60;
    font-family: "Inter", sans-serif;
  }
  .new-menu.on { display: block; }
  .new-menu a {
    display: block; padding: 8px 12px; border-radius: 8px;
    font-size: 13.5px; color: var(--ink-soft); cursor: pointer; font-weight: 500;
  }
  .new-menu a:hover { background: color-mix(in srgb, var(--ink) 8%, transparent); color: var(--ink); }
  .ws-teacher .av { width: 30px; height: 30px; border-radius: 50%; background: var(--ink); color: var(--bg); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; }
  .ws-teacher .tn { font-size: 13px; font-weight: 600; }
  .ws-teacher .ts { font-size: 11px; color: var(--muted); }

  .ws-main { padding: 28px 40px 80px; font-family: "Inter", sans-serif; }
  @media (max-width: 700px) { .ws-main { padding: 24px 20px 60px; } }
  .ws-top { display: flex; justify-content: space-between; align-items: center; gap: 20px; margin-bottom: 16px; }
  .ws-top .actions { display: flex; gap: 8px; }
  .ws-top .actions button { font-family: "Inter", sans-serif; font-size: 13px; padding: 8px 14px; border-radius: 999px; border: 1px solid var(--line-strong); background: transparent; color: var(--ink); cursor: pointer; font-weight: 500; }
  .ws-top .actions button.primary { background: var(--ink); color: var(--bg); border-color: var(--ink); font-weight: 600; }

  .ws-hello { font-family: "Fraunces", Georgia, serif; font-size: clamp(32px, 4vw, 44px); letter-spacing: -0.028em; line-height: 1.05; font-weight: 400; margin: 12px 0 6px; }
  .ws-hello .it { font-style: italic; font-weight: 300; }
  .ws-sub { color: var(--muted); font-size: 14px; margin-bottom: 32px; }

  .ws-page { display: none; }
  .ws-page.on { display: block; }
  .ph h1 { font-family: "Fraunces", Georgia, serif; font-size: clamp(32px, 4vw, 44px); letter-spacing: -0.028em; font-weight: 400; margin: 12px 0 6px; line-height: 1.05; }
  .ph h1 .it { font-style: italic; font-weight: 300; }
  .ph p { color: var(--muted); font-size: 14px; margin: 0 0 20px; }

  .control-note { padding: 14px 18px; border-radius: 12px; background: color-mix(in srgb, var(--ink) 6%, var(--bg-elev)); border-left: 3px solid var(--ink); font-size: 13.5px; margin-bottom: 20px; color: var(--ink-soft); }
  .control-note b { color: var(--ink); }

  .queue { border: 1px solid var(--line-strong); border-radius: 16px; overflow: hidden; background: color-mix(in srgb, var(--stamp) 6%, var(--bg-elev)); margin-bottom: 32px; }
  .queue-head { padding: 18px 22px; border-bottom: 1px solid var(--line); }
  .queue-head .t { font-family: "Fraunces", Georgia, serif; font-size: 20px; letter-spacing: -0.015em; font-weight: 500; }
  .queue-head .t .it { font-style: italic; }
  .qrow { display: grid; grid-template-columns: 1fr auto; gap: 18px; padding: 14px 22px; align-items: center; border-bottom: 1px solid var(--line); }
  .qrow:last-child { border-bottom: none; }
  .qrow .qi { font-size: 14px; font-weight: 600; }
  .qrow .qi .tag { display: inline-block; margin-right: 8px; font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 700; padding: 3px 7px; border-radius: 4px; background: color-mix(in srgb, var(--ink) 8%, transparent); color: var(--ink-soft); }
  .qrow .qs { font-size: 12px; color: var(--muted); }
  .qrow .qa { display: flex; gap: 6px; }
  .qrow .qa button { font-family: "Inter", sans-serif; font-size: 12px; padding: 6px 12px; border-radius: 999px; border: 1px solid var(--line-strong); background: transparent; color: var(--ink); cursor: pointer; font-weight: 600; }
  .qrow .qa button.approve { background: var(--ink); color: var(--bg); border-color: var(--ink); }
  @media (max-width: 700px) { .qrow { grid-template-columns: 1fr; gap: 8px; } }
  .cchip { display: inline-block; margin-left: 6px; font-family: "Inter", sans-serif; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 700; padding: 2px 7px; border-radius: 999px; background: color-mix(in srgb, var(--ink) 8%, transparent); color: var(--ink-soft); vertical-align: 1px; }

  .grid-label { font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase; color: var(--muted); margin: 8px 0 14px; }
  .tools { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
  @media (max-width: 900px) { .tools { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 560px) { .tools { grid-template-columns: 1fr; } }
  .tool { background: var(--bg-elev); border: 1px solid var(--line); border-radius: 14px; padding: 20px; min-height: 130px; display: flex; flex-direction: column; }
  .tool .ic { width: 34px; height: 34px; border-radius: 8px; background: color-mix(in srgb, var(--ink) 8%, transparent); display: flex; align-items: center; justify-content: center; font-family: "Fraunces", Georgia, serif; color: var(--ink); font-size: 16px; font-weight: 500; margin-bottom: 12px; font-style: italic; }
  .tool .tt { font-family: "Fraunces", Georgia, serif; font-size: 20px; letter-spacing: -0.015em; font-weight: 500; margin-bottom: 4px; line-height: 1.15; }
  .tool .td { font-size: 13px; color: var(--muted); line-height: 1.5; margin-top: auto; }

  .recent-list { display: flex; flex-direction: column; border: 1px solid var(--line); border-radius: 14px; overflow: hidden; background: var(--bg-elev); }
  .rrow { display: grid; grid-template-columns: 1fr auto; gap: 14px; padding: 14px 20px; align-items: center; border-bottom: 1px solid var(--line); }
  .rrow:last-child { border-bottom: none; }
  .rrow .name { font-weight: 600; font-size: 14px; }
  .rrow .meta { font-size: 12px; color: var(--muted); margin-top: 2px; }
  .rrow .status { font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 700; padding: 4px 10px; border-radius: 999px; }
  .st-draft { color: var(--ink-soft); background: color-mix(in srgb, var(--ink) 8%, transparent); }
  .st-review { color: var(--stamp); background: color-mix(in srgb, var(--stamp) 12%, transparent); }
  .st-out { color: var(--ok); background: color-mix(in srgb, var(--ok) 14%, transparent); }

  /* ask box (simple) */
  .ask-box { border: 1px solid var(--line-strong); border-radius: 14px; background: var(--bg-elev); padding: 16px 18px; margin-bottom: 18px; }
  .ask-label { font-family: "Inter", sans-serif; font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase; color: var(--muted); font-weight: 700; margin-bottom: 10px; }
  .ask-input { display: flex; align-items: center; gap: 10px; background: var(--bg); border: 1px solid var(--line); border-radius: 10px; padding: 8px 12px; }
  .ask-input:focus-within { border-color: var(--ink); }
  .ask-prompt { font-family: "Fraunces", Georgia, serif; font-size: 20px; color: var(--muted); font-weight: 300; }
  .ask-input input { flex: 1; border: none; outline: none; background: transparent; color: var(--ink); font-family: "Inter", sans-serif; font-size: 14.5px; padding: 6px 0; }
  .ask-go { font-family: "Inter", sans-serif; font-size: 13px; font-weight: 600; padding: 8px 14px; border-radius: 999px; background: var(--ink); color: var(--bg); border: 1px solid var(--ink); cursor: pointer; }

  /* worksheet */
  .worksheet { background: var(--paper); border: 1px solid var(--line-strong); border-radius: 14px; padding: 36px 40px; font-family: "Inter", sans-serif; color: var(--ink); margin-bottom: 14px; }
  .worksheet.mini { padding: 20px 22px; }
  .worksheet.mini p { font-size: 13.5px; line-height: 1.55; margin: 6px 0; }
  .ws-title { font-family: "Inter", sans-serif; font-size: 30px; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 12px; line-height: 1.05; }
  .ws-meta { font-family: "Inter", sans-serif; font-size: 13px; color: var(--ink-soft); display: flex; gap: 20px; flex-wrap: wrap; align-items: baseline; }
  .ws-meta .ln { display: inline-block; border-bottom: 1px dashed var(--line-strong); min-width: 140px; height: 1em; }
  .ws-meta .ln.sm { min-width: 90px; }
  .ws-meta .ln.xs { min-width: 60px; }
  .ws-hr { border: none; border-top: 1px solid var(--line-strong); margin: 18px 0 20px; }
  .ws-q { padding: 12px 0 16px; border-bottom: 1px dashed var(--line); }
  .ws-q:last-child { border-bottom: none; }
  .ws-qh { font-size: 14px; margin-bottom: 8px; display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }
  .ws-qh b { font-weight: 700; font-size: 15px; }
  .ws-qh .pts { color: var(--muted); font-weight: 500; }
  .ws-qh .qtype { color: var(--ink); font-weight: 700; }
  .ws-qb { font-size: 15px; line-height: 1.55; margin-bottom: 8px; }
  .ws-opts { padding-left: 24px; margin: 6px 0 0; }
  .ws-opts li { font-size: 14.5px; padding: 4px 0; }
  .ws-lines { display: flex; flex-direction: column; gap: 14px; margin-top: 8px; }
  .ws-lines .wl { border-bottom: 1px solid color-mix(in srgb, var(--ink) 18%, transparent); height: 18px; }
  .ws-graph { margin-top: 10px; height: 180px; border: 1px solid var(--line-strong); background: repeating-linear-gradient(to right, transparent 0, transparent 19px, color-mix(in srgb, var(--ink) 6%, transparent) 19px, color-mix(in srgb, var(--ink) 6%, transparent) 20px), repeating-linear-gradient(to bottom, transparent 0, transparent 19px, color-mix(in srgb, var(--ink) 6%, transparent) 19px, color-mix(in srgb, var(--ink) 6%, transparent) 20px); position: relative; }
  .ws-graph::before, .ws-graph::after { content: ""; position: absolute; background: var(--ink); }
  .ws-graph::before { left: 12px; top: 12px; bottom: 12px; width: 2px; }
  .ws-graph::after { left: 12px; right: 12px; bottom: 12px; height: 2px; }

  .doc-tag { font-size: 11px; text-transform: uppercase; letter-spacing: 0.18em; color: var(--muted); margin-bottom: 10px; }

  /* send-to */
  .send-to { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 12px 16px; border: 1px dashed var(--line-strong); border-radius: 12px; background: color-mix(in srgb, var(--ink) 3%, var(--bg-elev)); font-family: "Inter", sans-serif; margin-bottom: 12px; }
  .send-to .st-label { font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted); font-weight: 700; margin-right: 4px; }
  .prov { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; padding: 6px 10px 6px 8px; border-radius: 999px; border: 1px solid var(--line-strong); background: var(--bg); color: var(--ink); cursor: pointer; font-weight: 600; }
  .prov:hover { border-color: var(--ink); }
  .prov.on { background: var(--ink); color: var(--bg); border-color: var(--ink); }
  .prov .pi { width: 16px; height: 16px; border-radius: 4px; display: inline-flex; align-items: center; justify-content: center; font-family: "Fraunces", Georgia, serif; font-size: 10px; font-weight: 700; color: #fff; }
  .pi.canvas { background: #e13138; }
  .pi.classroom { background: #1a73e8; }
  .pi.forms { background: #7248b9; }
  .pi.pdf { background: #b7331f; }
  .pi.docx { background: #2b579a; }
  .pi.print { background: #4a5568; }

  .approve-bar { display: flex; gap: 8px; justify-content: flex-end; }
  .approve-bar button { font-family: "Inter", sans-serif; font-size: 13px; padding: 10px 18px; border-radius: 999px; border: 1px solid var(--line-strong); background: transparent; color: var(--ink); cursor: pointer; font-weight: 600; }
  .approve-bar button.primary { background: var(--ink); color: var(--bg); border-color: var(--ink); }

  /* rubric */
  .rubric-matrix { border: 1px solid var(--line); border-radius: 14px; overflow: hidden; background: var(--bg-elev); margin-bottom: 16px; }
  .rm-row { display: grid; grid-template-columns: 1.4fr 1fr 1fr 1fr 1fr; padding: 14px 18px; gap: 14px; border-bottom: 1px solid var(--line); font-size: 13px; }
  .rm-row:last-child { border-bottom: none; }
  .rm-head { font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted); font-weight: 600; background: color-mix(in srgb, var(--ink) 3%, transparent); }
  .rm-row .mm { font-size: 11px; color: var(--muted); margin-top: 2px; }

  /* lesson */
  .timeline { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
  .tl-row { display: grid; grid-template-columns: 110px 1fr; gap: 14px; }
  .tl-time { font-family: "Inter", sans-serif; font-size: 13px; color: var(--muted); padding-top: 14px; letter-spacing: 0.04em; font-weight: 600; }
  .tl-card { background: var(--bg-elev); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; font-size: 14px; }
  .tl-card .mm { font-size: 12.5px; color: var(--muted); margin-top: 4px; }

  /* passage */
  .passage { font-family: "Fraunces", Georgia, serif; font-size: 16px; line-height: 1.6; color: var(--ink); }
  .passage p { margin: 0 0 12px; }
  .passage b { font-weight: 600; color: var(--stamp); }

  /* slides */
  .slides { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
  @media (max-width: 900px) { .slides { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 500px) { .slides { grid-template-columns: 1fr; } }
  .slide { background: var(--bg-elev); border: 1px solid var(--line); border-radius: 12px; padding: 16px; min-height: 120px; display: flex; flex-direction: column; gap: 10px; }
  .slide .sn { font-family: "Inter", sans-serif; font-size: 10px; color: var(--muted); letter-spacing: 0.18em; font-weight: 600; }
  .slide .sc { font-family: "Fraunces", Georgia, serif; font-size: 15px; }
  .slide .sc .mm { font-family: "Inter", sans-serif; font-size: 12px; color: var(--muted); margin-top: 6px; }

  /* diff */
  .diff-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 16px; }
  @media (max-width: 900px) { .diff-grid { grid-template-columns: 1fr; } }
  .diff-col p { font-family: "Fraunces", Georgia, serif; font-size: 14px; line-height: 1.5; margin: 8px 0; }

  /* notes textarea */
  .msg-write { width: 100%; min-height: 240px; resize: vertical; background: transparent; border: none; outline: none; font-family: "Fraunces", Georgia, serif; font-size: 15px; line-height: 1.6; color: var(--ink); padding: 0; }
  .chips { display: flex; gap: 6px; flex-wrap: wrap; margin: 14px 0 0; }
  .chip { font-family: "Inter", sans-serif; font-size: 11px; padding: 5px 10px; border-radius: 999px; border: 1px solid var(--line); color: var(--muted); font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; }
  .chip.on { background: var(--ink); color: var(--bg); border-color: var(--ink); }

  /* standards */
  .std { background: var(--bg-elev); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }
  .std-cat { font-family: "Inter", sans-serif; font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); font-weight: 700; padding: 14px 20px; background: color-mix(in srgb, var(--ink) 4%, transparent); border-bottom: 1px solid var(--line); border-top: 1px solid var(--line); }
  .std-cat:first-child { border-top: none; }
  .std-row { display: grid; grid-template-columns: 100px 1fr auto; gap: 18px; padding: 14px 20px; border-bottom: 1px solid var(--line); font-size: 13.5px; align-items: center; }
  .std-row:last-child { border-bottom: none; }
  .std-row b { font-family: "Inter", sans-serif; font-weight: 700; font-size: 12.5px; letter-spacing: 0.02em; }
  .pill { font-size: 10px; padding: 3px 8px; border-radius: 999px; background: color-mix(in srgb, var(--ink) 8%, transparent); color: var(--ink-soft); font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
  .pill.ok { color: var(--ok); background: color-mix(in srgb, var(--ok) 14%, transparent); }

  /* integrations */
  .conn { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
  @media (max-width: 900px) { .conn { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 560px) { .conn { grid-template-columns: 1fr; } }
  .cn-card { background: var(--bg-elev); border: 1px solid var(--line); border-radius: 14px; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
  .cn-card .cn-top { display: flex; justify-content: space-between; align-items: center; }
  .cn-card .cn-icon { width: 36px; height: 36px; border-radius: 10px; display: inline-flex; align-items: center; justify-content: center; font-family: "Fraunces", Georgia, serif; font-size: 16px; font-weight: 700; color: #fff; }
  .cn-card .cn-status { font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 700; padding: 4px 8px; border-radius: 999px; }
  .cn-status.linked { color: var(--ok); background: color-mix(in srgb, var(--ok) 14%, transparent); }
  .cn-card .cn-name { font-family: "Fraunces", Georgia, serif; font-size: 18px; font-weight: 500; letter-spacing: -0.015em; margin-top: 4px; }
  .cn-card .cn-desc { font-size: 12.5px; color: var(--muted); line-height: 1.5; }

  /* settings */
  .settings { display: flex; flex-direction: column; gap: 20px; }
  .sblock { background: var(--bg-elev); border: 1px solid var(--line); border-radius: 14px; padding: 22px 24px; }
  .sblock h3 { font-family: "Fraunces", Georgia, serif; font-size: 20px; font-weight: 500; margin: 0 0 14px; letter-spacing: -0.015em; }
  .sblock .mm { font-size: 12.5px; color: var(--muted); margin-bottom: 10px; }
  .frow { display: grid; grid-template-columns: 160px 1fr; gap: 14px; align-items: center; margin-bottom: 10px; font-size: 13px; }
  .frow label { color: var(--muted); text-transform: uppercase; font-size: 11px; letter-spacing: 0.14em; font-weight: 600; }
  .frow input { width: 100%; padding: 10px 12px; border-radius: 8px; border: 1px solid var(--line-strong); background: var(--bg); color: var(--ink); font-family: "Inter", sans-serif; font-size: 13.5px; }
  .sblock textarea { width: 100%; padding: 12px 14px; border-radius: 10px; border: 1px solid var(--line-strong); background: var(--bg); color: var(--ink); font-family: "Inter", sans-serif; font-size: 13.5px; min-height: 80px; resize: vertical; }
  .toggle { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--line); font-size: 13.5px; }
  .toggle:last-child { border-bottom: none; }
  .toggle .sw { font-family: "Inter", sans-serif; font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 700; padding: 5px 10px; border-radius: 999px; border: 1px solid var(--line-strong); color: var(--muted); }
  .toggle .sw.on { background: var(--ok); color: #fff; border-color: var(--ok); }

  /* modal */
  .modal-veil { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: none; align-items: center; justify-content: center; z-index: 100; padding: 20px; }
  .modal-veil.on { display: flex; }
  .modal { background: var(--bg); border-radius: 20px; border: 1px solid var(--line-strong); padding: 32px; width: 100%; max-width: 400px; font-family: "Inter", sans-serif; }
  .modal h3 { font-family: "Fraunces", Georgia, serif; font-size: 28px; letter-spacing: -0.02em; font-weight: 400; margin: 0 0 6px; }
  .modal h3 .it { font-style: italic; font-weight: 300; }
  .modal p { color: var(--muted); font-size: 14px; margin: 0 0 22px; }
  .modal label { display: block; font-size: 12px; font-weight: 600; margin-bottom: 6px; }
  .modal input { width: 100%; padding: 12px 14px; border-radius: 10px; border: 1px solid var(--line-strong); background: var(--bg-elev); color: var(--ink); font-size: 14px; font-family: "Inter", sans-serif; margin-bottom: 14px; }
  .modal .go { width: 100%; padding: 12px; border-radius: 999px; background: var(--ink); color: var(--bg); border: none; font-size: 14px; font-weight: 600; cursor: pointer; font-family: "Inter", sans-serif; }
  .modal .fine { text-align: center; margin-top: 14px; font-size: 12px; color: var(--muted); }
  .modal-err { color: var(--stamp); font-size: 12.5px; font-weight: 600; min-height: 18px; margin-bottom: 10px; }
  .auth-tabs { display: flex; gap: 6px; margin-bottom: 22px; }
  .auth-tab {
    flex: 1; padding: 10px 12px; border-radius: 999px;
    border: 1px solid var(--line-strong); background: transparent; color: var(--muted);
    font-family: "Inter", sans-serif; font-size: 13px; font-weight: 600; cursor: pointer;
    letter-spacing: 0.02em;
  }
  .auth-tab.on { background: var(--ink); color: var(--bg); border-color: var(--ink); }
  .auth-pane.hidden { display: none; }
  .auth-pane p a { color: var(--ink); text-decoration: underline; }
  .admin-shortcut { margin-top: 12px; text-align: center; font-family: "Inter", sans-serif; font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; font-weight: 700; }
  .admin-shortcut a { color: var(--stamp); text-decoration: none; padding: 6px 12px; border: 1px dashed var(--stamp); border-radius: 999px; }
  .admin-shortcut a:hover { background: color-mix(in srgb, var(--stamp) 10%, transparent); }
  .modal-lg { max-width: 720px; }
  .ai-head { display: flex; justify-content: space-between; align-items: flex-start; }
  .ai-head h3 { margin-bottom: 14px; }
  .ai-close { background: transparent; border: none; color: var(--muted); font-size: 22px; cursor: pointer; line-height: 1; }
  .ai-close:hover { color: var(--ink); }
  .ai-state { display: flex; gap: 12px; align-items: center; padding: 10px 0 14px; }
  .ai-state.hidden { display: none; }
  .ai-spinner { width: 18px; height: 18px; border: 2px solid var(--line-strong); border-top-color: var(--ink); border-radius: 50%; animation: ai-spin 0.8s linear infinite; }
  @keyframes ai-spin { to { transform: rotate(360deg); } }
  .ai-status { font-size: 13px; color: var(--muted); font-weight: 500; }
  textarea.ai-body {
    background: var(--paper); border: 1px solid var(--line); border-radius: 12px;
    padding: 20px 22px; height: 44vh; min-height: 240px; max-height: 55vh;
    font-family: "Fraunces", Georgia, serif; font-size: 15px; line-height: 1.6;
    color: var(--ink); white-space: pre-wrap; margin-bottom: 14px;
    width: 100%; resize: vertical; outline: none;
    display: block;
  }
  textarea.ai-body:focus { border-color: var(--ink); }
  textarea.ai-body.hidden { display: none; }
  .ai-sub { font-family: "Inter", sans-serif; font-size: 12.5px; color: var(--muted); margin-top: 2px; }
  .ai-foot .ai-approve { background: var(--ok); color: #fff; border-color: var(--ok); }

  /* empty state */
  .empty {
    padding: 60px 40px; text-align: center;
    border: 1px dashed var(--line-strong); border-radius: 18px;
    background: var(--bg-elev); font-family: "Inter", sans-serif;
    margin-bottom: 24px;
  }
  .empty-icon {
    width: 60px; height: 60px; margin: 0 auto 18px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 16px; background: color-mix(in srgb, var(--ink) 8%, transparent);
    font-family: "Fraunces", Georgia, serif; font-size: 34px; font-weight: 400; color: var(--ink);
  }
  .empty-title {
    font-family: "Fraunces", Georgia, serif; font-size: 28px; letter-spacing: -0.02em;
    font-weight: 500; margin-bottom: 8px;
  }
  .empty-title .it { font-style: italic; font-weight: 300; }
  .empty-body {
    font-size: 14px; color: var(--muted); max-width: 44ch; line-height: 1.55;
    margin: 0 auto 24px;
  }
  .empty-cta { margin: 0 auto; }
  .ai-foot { display: flex; gap: 8px; justify-content: flex-end; }
  .ai-foot button {
    font-family: "Inter", sans-serif; font-size: 13px; padding: 10px 16px; border-radius: 999px;
    border: 1px solid var(--line-strong); background: transparent; color: var(--ink); cursor: pointer; font-weight: 600;
  }
  .ai-foot .ai-use { background: var(--ink); color: var(--bg); border-color: var(--ink); }
  .ai-foot button:disabled { opacity: 0.5; cursor: not-allowed; }
  .ask-go:disabled { opacity: 0.6; cursor: wait; }

  /* toast */
  .toast {
    position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%) translateY(20px);
    background: var(--ink); color: var(--bg);
    border-radius: 999px; padding: 12px 16px 12px 14px;
    display: none; align-items: center; gap: 12px;
    font-family: "Inter", sans-serif; font-size: 13.5px; font-weight: 600;
    box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4);
    z-index: 150; opacity: 0; transition: opacity .25s ease, transform .25s ease;
  }
  .toast.on { display: flex; opacity: 1; transform: translateX(-50%) translateY(0); }
  .toast-tick { width: 22px; height: 22px; border-radius: 50%; background: var(--ok); color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; }
  .toast-undo { font-family: "Inter", sans-serif; font-size: 12px; font-weight: 700; padding: 5px 12px; border-radius: 999px; background: transparent; color: var(--bg); border: 1px solid color-mix(in srgb, var(--bg) 40%, transparent); cursor: pointer; letter-spacing: 0.04em; text-transform: uppercase; }
  .toast-undo:hover { background: color-mix(in srgb, var(--bg) 12%, transparent); }

  /* qrow fade after approve */
  .qrow.gone { opacity: 0.35; transition: opacity .3s ease; }

  /* class list */
  .class-list { display: none; margin: -14px 0 22px; border: 1px solid var(--line); border-radius: 10px; overflow: hidden; background: var(--bg-elev); }
  .class-list.on { display: block; }
  .cl-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border-bottom: 1px solid var(--line); cursor: pointer; font-size: 13px; }
  .cl-row:last-child { border-bottom: none; }
  .cl-row:hover { background: color-mix(in srgb, var(--ink) 5%, transparent); }
  .cl-row.on { background: color-mix(in srgb, var(--ink) 8%, transparent); }
  .cl-n b { font-weight: 600; }
  .cl-m { font-size: 11px; color: var(--muted); margin-top: 1px; }
  .cl-row.add { color: var(--muted); justify-content: center; font-weight: 600; }
  .ws-class { cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
  .ws-class .chev { color: var(--muted); font-size: 12px; transition: transform .2s ease; }
  .ws-class.open .chev { transform: rotate(180deg); }
</style>
'''

LANDING = r'''
<div id="landing">
<nav class="nav">
  <div class="wrap nav-in">
    <a class="brand" href="#top"><div class="brand-mark"></div><span>Atom Edu</span></a>
    <div class="nav-right">
      <a class="nav-link" href="#how">How it works</a>
      <a class="nav-link" href="#inside">Inside</a>
      <a class="nav-link" href="/privacy/">Privacy</a>
      <a class="nav-link" href="/terms/">Terms</a>
      <button class="nav-link ghost" data-signin>Sign in</button>
      <button class="nav-cta" data-signup>Get started</button>
    </div>
  </div>
</nav>

<section class="hero" id="top">
  <div class="wrap">
    <div class="eyebrow"><span class="dot"></span>For teachers</div>
    <h1 class="headline">Atom drafts. <span class="it">You approve.</span> Every time.</h1>
    <p class="lede sans">Atom drafts the worksheet, the quiz, the rubric, the note home. You edit and approve every piece. Nothing goes out until you say yes.</p>
    <div class="cta-row">
      <button class="btn" data-signup>Get started <span class="arrow">&rarr;</span></button>
      <a class="btn ghost" href="#how">See how it works</a>
    </div>
    <div class="fine">Free forever. No card.</div>
  </div>
</section>

<section class="section" id="how">
  <div class="wrap">
    <div class="section-label">How it works</div>
    <h2 class="big">Draft. Review. <span class="it">Approve.</span></h2>
    <div class="flow">
      <div class="step"><div class="step-num">01</div><h3>Give it the <span class="it">rough shape.</span></h3><p>A standard, a topic, a worksheet you already use.</p></div>
      <div class="step review"><span class="stamp">Required</span><div class="step-num">02</div><h3>Rewrite in <span class="it">your voice.</span></h3><p>You are the one writing the assignment. Atom is the messy first pass.</p></div>
      <div class="step"><div class="step-num">03</div><h3>Approve, and it <span class="it">is yours.</span></h3><p>Download it, print it, or copy it out. You decide how it reaches students.</p></div>
    </div>
  </div>
</section>

<section class="section" id="inside">
  <div class="wrap">
    <div class="section-label">Inside the workspace</div>
    <h2 class="big">Everything a teacher makes, <span class="it">in one place.</span></h2>
    <div class="tiles">
      <div class="tile"><div class="tn">Assignment <span class="it">maker</span></div><div class="tp">Printable worksheets with name, date, period, and point values.</div></div>
      <div class="tile"><div class="tn">Quiz &amp; test <span class="it">builder</span></div><div class="tp">Mix multiple choice, short answer, and diagrams.</div></div>
      <div class="tile"><div class="tn">Rubric <span class="it">builder</span></div><div class="tp">Rows tied to a standard. Attach to any assignment.</div></div>
      <div class="tile"><div class="tn">Slides &amp; <span class="it">boards</span></div><div class="tp">Slides for the projector, notes for the board.</div></div>
      <div class="tile"><div class="tn">Docs &amp; <span class="it">handouts</span></div><div class="tp">Family letters, syllabi, permission slips.</div></div>
      <div class="tile"><div class="tn">Reading <span class="it">passages</span></div><div class="tp">Leveled to your class. Questions attached.</div></div>
      <div class="tile"><div class="tn">Lesson <span class="it">planner</span></div><div class="tp">One class, or a full unit.</div></div>
      <div class="tile"><div class="tn">Notes <span class="it">home</span></div><div class="tp">You write it. Atom tone checks and drafts a translation.</div></div>
      <div class="tile"><div class="tn">Differentia<span class="it">tion</span></div><div class="tp">Same assignment, adapted for reading level, IEP, ELL.</div></div>
    </div>
  </div>
</section>

<section class="free">
  <div class="wrap">
    <div class="kicker">A promise</div>
    <h2 class="huge">Free, <span class="it">forever.</span></h2>
    <p class="caption">Every feature. Every classroom. Every year you keep teaching.</p>
  </div>
</section>

<section class="end">
  <div class="wrap">
    <h2 class="tag">Atom drafts. <span class="it">You approve.</span> Every time.</h2>
    <button class="btn" data-signup>Get started <span class="arrow">&rarr;</span></button>
  </div>
</section>

<footer class="ft">
  <div class="wrap ft-row">
    <div class="brand"><div class="brand-mark"></div><span>Atom Edu</span></div>
    <div class="ft-links">
      <a href="#how">How it works</a>
      <a href="#inside">Inside</a>
      <a href="/privacy/">Privacy</a>
      <a href="/terms/">Terms</a>
      <a href="mailto:hello@atom-edu.org">Contact</a>
    </div>
    <div>&copy; Atom Edu</div>
  </div>
</footer>
</div>
'''

MODAL = r'''
<div class="modal-veil" id="modal">
  <div class="modal">
    <div class="auth-tabs">
      <button class="auth-tab" data-tab="signin">Sign in</button>
      <button class="auth-tab on" data-tab="signup">Sign up</button>
    </div>

    <div class="auth-pane" id="pane-signup">
      <h3>Come on <span class="it">in.</span></h3>
      <p>New here? Set up in about 30 seconds. Verified by a school (.edu) or organization (.org) email.</p>
      <label>Your name</label>
      <input id="in-name" placeholder="Ms. Chen" autocomplete="name">
      <label>School email</label>
      <input id="in-email" placeholder="you@school.edu" type="email" autocomplete="email">
      <label>What you teach</label>
      <input id="in-class" placeholder="6th grade Science" autocomplete="off">
      <div class="modal-err" id="modal-err"></div>
      <button class="go" id="go">Create my workspace</button>
      <div class="fine">Free forever. Email is used only to authorize drafts.</div>
    </div>

    <div class="auth-pane hidden" id="pane-signin">
      <h3>Welcome <span class="it">back.</span></h3>
      <p>Type the email you signed up with.</p>
      <label>School email</label>
      <input id="si-email" placeholder="you@school.edu" type="email" autocomplete="email">
      <div class="modal-err" id="si-err"></div>
      <button class="go" id="si-go">Sign in</button>
      <div class="fine">Sign in works on any browser where you set up before. New device? Just <a href="#" data-switch-tab="signup">sign up</a> again.</div>
      <div class="admin-shortcut"><a href="#" id="admin-login">Test as admin</a></div>
    </div>
  </div>
</div>

<div class="modal-veil" id="ai-modal">
  <div class="modal modal-lg">
    <div class="ai-head">
      <div>
        <h3 id="ai-title">Your <span class="it">draft.</span></h3>
        <div class="ai-sub" id="ai-sub">Edit anything before you save.</div>
      </div>
      <button class="ai-close" id="ai-close" aria-label="Close">&times;</button>
    </div>
    <div class="ai-state" id="ai-state">
      <div class="ai-spinner"></div>
      <div class="ai-status" id="ai-status">Drafting with Atom&hellip;</div>
    </div>
    <textarea class="ai-body" id="ai-body" placeholder="Waiting for Atom&hellip;"></textarea>
    <div class="ai-foot">
      <button class="ai-regen" id="ai-regen">Regenerate</button>
      <button class="ai-copy" id="ai-copy">Copy</button>
      <button class="ai-approve" id="ai-approve">Approve &amp; save</button>
      <button class="ai-use" id="ai-use">Save as draft</button>
    </div>
  </div>
</div>
'''

SIDEBAR = r'''
<aside class="ws-side">
  <div class="ws-brand" data-nav="home"><div class="brand-mark"></div><span>Atom Edu</span></div>
  <div class="ws-class" id="ws-class-toggle">
    <div>
      <div class="cn" id="ws-class-name">6th grade Science</div>
      <div class="cp">Period 3</div>
    </div>
    <div class="chev">&#9662;</div>
  </div>
  <div class="class-list" id="class-list">
    <div class="cl-row on"><div class="cl-n"><b>Period 3</b><div class="cl-m">Science, honors</div></div></div>
    <div class="cl-row"><div class="cl-n"><b>Period 1</b><div class="cl-m">Science</div></div></div>
    <div class="cl-row"><div class="cl-n"><b>Period 2</b><div class="cl-m">Science</div></div></div>
    <div class="cl-row"><div class="cl-n"><b>Period 5</b><div class="cl-m">Science</div></div></div>
    <div class="cl-row add">+ Add a class</div>
  </div>

  <div class="ws-nav-label">Workspace</div>
  <div class="ws-nav">
    <a data-nav="home"><span class="lbl">Home</span></a>
    <a data-nav="queue"><span class="lbl">Approval queue</span></a>
    <a data-nav="classes"><span class="lbl">Classes</span></a>
  </div>

  <div class="ws-nav-label">Make</div>
  <div class="ws-nav">
    <a data-nav="assignment"><span class="lbl">Assignment maker</span></a>
    <a data-nav="quiz"><span class="lbl">Quiz builder</span></a>
    <a data-nav="rubric"><span class="lbl">Rubric builder</span></a>
    <a data-nav="slides"><span class="lbl">Slides &amp; boards</span></a>
    <a data-nav="docs"><span class="lbl">Docs &amp; handouts</span></a>
    <a data-nav="passages"><span class="lbl">Reading passages</span></a>
    <a data-nav="lesson"><span class="lbl">Lesson planner</span></a>
  </div>

  <div class="ws-nav-label">Respond</div>
  <div class="ws-nav">
    <a data-nav="notes"><span class="lbl">Notes home</span></a>
    <a data-nav="diff"><span class="lbl">Differentiation</span></a>
  </div>

  <div class="ws-nav-label">You</div>
  <div class="ws-nav">
    <a data-nav="standards"><span class="lbl">Standards library</span></a>
    <a data-nav="settings"><span class="lbl">Settings</span></a>
  </div>

  <div class="ws-teacher" id="ws-teacher"><div class="av" id="av-init">MC</div><div class="ws-teacher-info"><div class="tn" id="av-name">Ms. Chen</div><div class="ts">Signed in</div></div><button class="signout" id="signout" title="Sign out">&#x21E5;</button></div>
</aside>
'''

WORKSPACE = r'''
<div id="workspace" class="hidden">
  <div class="ws-shell">
    ''' + SIDEBAR + r'''
    <main class="ws-main">
      <div class="ws-top">
        <div></div>
        <div class="actions">
          <div class="new-wrap">
            <button class="primary" id="new-draft-btn">+ New draft</button>
            <div class="new-menu" id="new-menu">
              <a data-nav="assignment">Assignment</a>
              <a data-nav="quiz">Quiz or test</a>
              <a data-nav="rubric">Rubric</a>
              <a data-nav="lesson">Lesson plan</a>
              <a data-nav="passages">Reading passage</a>
              <a data-nav="slides">Slide deck</a>
              <a data-nav="docs">Doc or handout</a>
              <a data-nav="notes">Note home</a>
              <a data-nav="diff">Differentiation</a>
            </div>
          </div>
          <button class="theme-toggle" data-tt style="font-size:12px;">Theme</button>
        </div>
      </div>
      ''' + all_pages + r'''
    </main>
  </div>
  <div class="toast" id="toast"><span class="toast-tick">&check;</span><span id="toast-text">Approved.</span><button class="toast-undo" id="toast-undo">Undo</button></div>
</div>
'''

SCRIPT = r'''
<script>
  var WORKER_URL = 'https://atom-edu.pritamavuthu7.workers.dev';
  var DEFAULT_MODEL = 'llama-3.3-70b-versatile';
  (function(){
    var root = document.documentElement;
    function apply(mode){
      if(mode === 'dark') root.setAttribute('data-theme','dark');
      else if(mode === 'light') root.setAttribute('data-theme','light');
      else root.removeAttribute('data-theme');
    }
    try { var saved = localStorage.getItem('atom-theme'); if(saved) apply(saved); } catch(e){}
    document.querySelectorAll('[data-tt]').forEach(function(b){
      b.addEventListener('click', function(){
        var current = root.getAttribute('data-theme');
        var next = current === 'dark' ? 'light' : 'dark';
        apply(next);
        try { localStorage.setItem('atom-theme', next); } catch(e){}
      });
    });

    var veil = document.getElementById('modal');
    function switchAuthTab(name){
      document.querySelectorAll('.auth-tab').forEach(function(t){
        t.classList.toggle('on', t.getAttribute('data-tab') === name);
      });
      document.getElementById('pane-signup').classList.toggle('hidden', name !== 'signup');
      document.getElementById('pane-signin').classList.toggle('hidden', name !== 'signin');
      var e = document.getElementById('modal-err'); if(e) e.textContent = '';
      var e2 = document.getElementById('si-err'); if(e2) e2.textContent = '';
    }
    document.querySelectorAll('.auth-tab').forEach(function(t){
      t.addEventListener('click', function(){ switchAuthTab(t.getAttribute('data-tab')); });
    });
    document.querySelectorAll('[data-switch-tab]').forEach(function(a){
      a.addEventListener('click', function(e){ e.preventDefault(); switchAuthTab(a.getAttribute('data-switch-tab')); });
    });
    function openModal(tab){ switchAuthTab(tab || 'signup'); veil.classList.add('on'); setTimeout(function(){ var i = document.querySelector((tab==='signin'?'#si-email':'#in-name')); if(i) i.focus(); }, 30); }
    document.querySelectorAll('[data-signup]').forEach(function(b){ b.addEventListener('click', function(){ openModal('signup'); }); });
    document.querySelectorAll('[data-signin]').forEach(function(b){ b.addEventListener('click', function(){ openModal('signin'); }); });
    document.querySelectorAll('[data-open]').forEach(function(b){ b.addEventListener('click', function(){ openModal('signup'); }); });
    veil.addEventListener('click', function(e){ if(e.target === veil) veil.classList.remove('on'); });

    function initials(name){
      if(!name) return 'T';
      var p = name.trim().split(/\s+/);
      return (p[0][0] + (p[p.length-1][0] || '')).toUpperCase();
    }
    function goto(page){
      document.querySelectorAll('.ws-page').forEach(function(p){ p.classList.remove('on'); });
      var target = document.querySelector('.ws-page[data-page="'+page+'"]');
      if(target) target.classList.add('on');
      document.querySelectorAll('.ws-nav a').forEach(function(a){ a.classList.remove('on'); });
      var link = document.querySelector('.ws-nav a[data-nav="'+page+'"]');
      if(link) link.classList.add('on');
      window.scrollTo(0, 0);
    }
    document.querySelectorAll('[data-nav]').forEach(function(a){ a.addEventListener('click', function(){ goto(a.getAttribute('data-nav')); }); });

    function enterWorkspace(name, cls, email){
      name = name || 'Ms. Chen';
      cls = cls || '6th grade Science';
      document.getElementById('hello-name').textContent = name;
      document.getElementById('av-name').textContent = name;
      document.getElementById('av-init').textContent = initials(name);
      document.getElementById('ws-class-name').textContent = cls;
      veil.classList.remove('on');
      document.getElementById('landing').classList.add('hidden');
      document.getElementById('workspace').classList.remove('hidden');
      goto('home');
      try {
        localStorage.setItem('atom-user', JSON.stringify({name:name, cls:cls, email:email || ''}));
        if(email) localStorage.setItem('atom-email', email);
      } catch(e){}
      renderAll();
    }
    function getUserEmail(){
      try {
        var e = localStorage.getItem('atom-email');
        if(e && EMAIL_RX.test(e)) return e;
        var u = JSON.parse(localStorage.getItem('atom-user') || 'null');
        if(u && u.email && EMAIL_RX.test(u.email)) return u.email;
      } catch(e){}
      return '';
    }
    var EMAIL_RX = /^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.(edu|org)$/i;
    var ADMIN_EMAIL = 'admin@atom-edu.org';
    var ADMIN_NAME  = 'Test Admin';
    var ADMIN_CLS   = 'Test class, all grades';
    function loginAsAdmin(){
      saveKnownUser({ name: ADMIN_NAME, email: ADMIN_EMAIL, cls: ADMIN_CLS });
      enterWorkspace(ADMIN_NAME, ADMIN_CLS, ADMIN_EMAIL);
    }
    var adminBtn = document.getElementById('admin-login');
    if(adminBtn){ adminBtn.addEventListener('click', function(e){ e.preventDefault(); loginAsAdmin(); }); }
    // Store known users by email (localStorage-only per browser).
    function saveKnownUser(u){
      try {
        var known = JSON.parse(localStorage.getItem('atom-known') || '{}');
        known[u.email.toLowerCase()] = { name: u.name, cls: u.cls };
        localStorage.setItem('atom-known', JSON.stringify(known));
      } catch(e){}
    }
    function findKnownUser(email){
      try {
        var known = JSON.parse(localStorage.getItem('atom-known') || '{}');
        return known[(email||'').toLowerCase()] || null;
      } catch(e){ return null; }
    }
    // Sign in submit
    var siGo = document.getElementById('si-go');
    if(siGo){
      siGo.addEventListener('click', function(){
        var email = document.getElementById('si-email').value.trim();
        var err = document.getElementById('si-err');
        err.textContent = '';
        if(!EMAIL_RX.test(email)){ err.textContent = 'A .edu or .org email is required.'; return; }
        if(email.toLowerCase() === ADMIN_EMAIL){ loginAsAdmin(); return; }
        var known = findKnownUser(email);
        if(!known){
          err.textContent = 'No account found on this browser. Sign up instead.';
          setTimeout(function(){
            switchAuthTab('signup');
            document.getElementById('in-email').value = email;
            document.getElementById('in-name').focus();
          }, 900);
          return;
        }
        enterWorkspace(known.name, known.cls, email);
      });
      document.getElementById('si-email').addEventListener('keydown', function(e){ if(e.key === 'Enter') siGo.click(); });
    }
    // Sign up submit
    document.getElementById('go').addEventListener('click', function(){
      var name = document.getElementById('in-name').value.trim();
      var email = document.getElementById('in-email').value.trim();
      var cls = document.getElementById('in-class').value.trim();
      var err = document.getElementById('modal-err');
      err.textContent = '';
      if(!name){ err.textContent = 'Please enter your name.'; return; }
      if(!EMAIL_RX.test(email)){ err.textContent = 'A school (.edu) or organization (.org) email is required.'; return; }
      if(!cls){ err.textContent = 'What do you teach?'; return; }
      try { localStorage.setItem('atom-email', email); } catch(e){}
      saveKnownUser({ name: name, email: email, cls: cls });
      enterWorkspace(name, cls, email);
    });
    // Also allow Enter on signup fields
    ['in-name','in-email','in-class'].forEach(function(id){
      var el = document.getElementById(id);
      if(el) el.addEventListener('keydown', function(e){ if(e.key === 'Enter') document.getElementById('go').click(); });
    });
    try {
      var u = JSON.parse(localStorage.getItem('atom-user') || 'null');
      if(u && u.name){
        document.getElementById('hello-name').textContent = u.name;
        document.getElementById('av-name').textContent = u.name;
        document.getElementById('av-init').textContent = initials(u.name);
        document.getElementById('ws-class-name').textContent = u.cls || '6th grade Science';
      }
    } catch(e){}

    // Toast
    var toast = document.getElementById('toast');
    var toastText = document.getElementById('toast-text');
    var toastTimer = null;
    var lastApprovedRow = null;
    function showToast(msg){
      toastText.textContent = msg || 'Approved.';
      toast.classList.add('on');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(function(){ toast.classList.remove('on'); }, 5000);
    }
    document.getElementById('toast-undo').addEventListener('click', function(){
      if(lastApprovedId){
        updateDraft(lastApprovedId, { status: 'awaiting', approvedAt: null });
      }
      toast.classList.remove('on');
      showToast('Pulled back to draft.');
    });

    // Approve buttons on maker pages (visual, opens ask box if empty)
    document.querySelectorAll('.approve-bar .primary').forEach(function(b){
      b.addEventListener('click', function(){ showToast('Approved. Saved to your workspace.'); });
    });
    document.querySelectorAll('.approve-bar button:not(.primary)').forEach(function(b){
      b.addEventListener('click', function(){ showToast('Returned to draft.'); });
    });

    // Empty state CTA on Home
    document.querySelectorAll('[data-empty-cta]').forEach(function(b){
      b.addEventListener('click', function(){
        var menu = document.getElementById('new-menu');
        if(menu) menu.classList.add('on');
      });
    });

    // Tabs
    document.querySelectorAll('.tabs').forEach(function(tabs){
      tabs.querySelectorAll('.tab').forEach(function(t){
        t.addEventListener('click', function(){
          tabs.querySelectorAll('.tab').forEach(function(x){ x.classList.remove('on'); });
          t.classList.add('on');
        });
      });
    });

    // Provider chips (send-to)
    document.querySelectorAll('.send-to').forEach(function(bar){
      bar.querySelectorAll('.prov').forEach(function(p){
        p.addEventListener('click', function(){
          bar.querySelectorAll('.prov').forEach(function(x){ x.classList.remove('on'); });
          p.classList.add('on');
        });
      });
    });

    // Chip toggles (EN / ES etc)
    document.querySelectorAll('.chips').forEach(function(bar){
      bar.querySelectorAll('.chip').forEach(function(c){
        c.addEventListener('click', function(){
          bar.querySelectorAll('.chip').forEach(function(x){ x.classList.remove('on'); });
          c.classList.add('on');
        });
      });
    });

    // ===== Draft store (localStorage) =====
    var DRAFTS_KEY = 'atom-drafts';
    function loadDrafts(){
      try { return JSON.parse(localStorage.getItem(DRAFTS_KEY) || '[]'); } catch(e){ return []; }
    }
    function saveDrafts(list){
      try { localStorage.setItem(DRAFTS_KEY, JSON.stringify(list)); } catch(e){}
    }
    function randomId(){
      return 'd_' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);
    }
    function addDraft(d){
      var list = loadDrafts();
      d.id = randomId();
      d.createdAt = new Date().getTime();
      list.unshift(d);
      saveDrafts(list);
      renderAll();
      return d.id;
    }
    function updateDraft(id, changes){
      var list = loadDrafts();
      for(var i=0;i<list.length;i++){ if(list[i].id === id){ Object.assign(list[i], changes); break; } }
      saveDrafts(list);
      renderAll();
    }
    function deleteDraft(id){
      var list = loadDrafts().filter(function(d){ return d.id !== id; });
      saveDrafts(list); renderAll();
    }
    function findDraft(id){ return loadDrafts().find(function(d){ return d.id === id; }); }

    var TYPE_META = {
      assignment: { tag: 'Assignment', page: 'assignment' },
      quiz:       { tag: 'Quiz', page: 'quiz' },
      rubric:     { tag: 'Rubric', page: 'rubric' },
      lesson:     { tag: 'Lesson', page: 'lesson' },
      passages:   { tag: 'Passage', page: 'passages' },
      slides:     { tag: 'Slides', page: 'slides' },
      docs:       { tag: 'Doc', page: 'docs' },
      notes:      { tag: 'Note home', page: 'notes' },
      diff:       { tag: 'Differentiation', page: 'diff' }
    };
    function tagFor(t){ return (TYPE_META[t] && TYPE_META[t].tag) || 'Draft'; }
    function escapeHTML(s){ return String(s||'').replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }

    function titleFrom(content, prompt){
      if(!content) return prompt || 'Untitled draft';
      var lines = content.split(/\n+/);
      for(var i=0;i<lines.length;i++){
        var l = lines[i].trim().replace(/^[#*\-\s]+/, '').replace(/[*_`]/g,'');
        if(l && l.length < 90) return l;
      }
      return (prompt || 'Untitled draft').slice(0, 80);
    }

    // ===== Renderers =====
    function renderAll(){
      renderHome();
      renderQueuePage();
    }
    function renderHome(){
      var drafts = loadDrafts();
      var awaiting = drafts.filter(function(d){ return d.status === 'awaiting'; });
      var awaitingBox = document.getElementById('home-awaiting');
      var recentWrap = document.getElementById('home-recent-wrap');
      var recentBox  = document.getElementById('home-recent');
      var empty = document.getElementById('home-empty');
      var sub = document.getElementById('home-sub');
      if(!awaitingBox) return;

      if(drafts.length === 0){
        awaitingBox.innerHTML = '';
        recentWrap.style.display = 'none';
        empty.style.display = 'block';
        sub.textContent = 'Nothing here yet. Start your first draft.';
        return;
      }
      empty.style.display = 'none';
      sub.textContent = 'Everything you draft with Atom lives here.';

      if(awaiting.length){
        awaitingBox.innerHTML =
          '<div class="queue"><div class="queue-head"><div class="t">Awaiting <span class="it">your yes</span></div></div>' +
          awaiting.map(qrowHTML).join('') + '</div>';
        wireQrow(awaitingBox);
      } else {
        awaitingBox.innerHTML =
          '<div class="empty" style="padding: 34px 30px;">' +
          '<div class="empty-title" style="font-size:22px;">All clear.</div>' +
          '<div class="empty-body" style="margin-bottom:0;">Nothing awaiting your yes right now.</div>' +
          '</div>';
      }

      recentWrap.style.display = 'block';
      recentBox.innerHTML = drafts.slice(0, 10).map(rrowHTML).join('');
      wireRrow(recentBox);
    }
    function renderQueuePage(){
      var drafts = loadDrafts();
      var awaiting = drafts.filter(function(d){ return d.status === 'awaiting'; });
      var sent = drafts.filter(function(d){ return d.status === 'sent'; }).slice(0, 20);
      var list = document.getElementById('queue-list');
      var empty = document.getElementById('queue-empty');
      var sentWrap = document.getElementById('queue-sent-wrap');
      var sentBox  = document.getElementById('queue-sent');
      if(!list) return;
      if(awaiting.length === 0){
        list.innerHTML = '';
        empty.style.display = 'block';
      } else {
        empty.style.display = 'none';
        list.innerHTML =
          '<div class="queue"><div class="queue-head"><div class="t">Needs <span class="it">you</span></div></div>' +
          awaiting.map(qrowHTML).join('') + '</div>';
        wireQrow(list);
      }
      if(sent.length){
        sentWrap.style.display = 'block';
        sentBox.innerHTML = sent.map(rrowHTML).join('');
        wireRrow(sentBox);
      } else {
        sentWrap.style.display = 'none';
      }
    }
    function qrowHTML(d){
      var cls = d.class ? ' <span class="cchip">' + escapeHTML(d.class) + '</span>' : '';
      return '<div class="qrow" data-id="' + d.id + '">' +
        '<div>' +
          '<div class="qi"><span class="tag">' + escapeHTML(tagFor(d.type)) + '</span>' + escapeHTML(d.title || 'Untitled') + cls + '</div>' +
          '<div class="qs">Draft ready</div>' +
        '</div>' +
        '<div class="qa"><button class="js-open">Open &amp; edit</button><button class="approve">Approve</button></div>' +
      '</div>';
    }
    function rrowHTML(d){
      var cls = d.class ? ' <span class="cchip">' + escapeHTML(d.class) + '</span>' : '';
      var statusCls = d.status === 'sent' ? 'st-out' : d.status === 'awaiting' ? 'st-review' : 'st-draft';
      var statusText = d.status === 'sent' ? 'Sent' : d.status === 'awaiting' ? 'Awaiting yes' : 'Draft';
      var meta = d.status === 'sent'
        ? 'Approved ' + timeAgo(d.approvedAt || d.createdAt)
        : 'Created ' + timeAgo(d.createdAt);
      return '<div class="rrow" data-id="' + d.id + '">' +
        '<div><div class="name">' + escapeHTML(d.title || 'Untitled') + cls + '</div><div class="meta">' + meta + '</div></div>' +
        '<div class="status ' + statusCls + '">' + statusText + '</div>' +
      '</div>';
    }
    function timeAgo(ts){
      if(!ts) return '';
      var s = Math.max(1, Math.floor((Date.now() - ts) / 1000));
      if(s < 60) return 'just now';
      if(s < 3600) return Math.floor(s/60) + ' min ago';
      if(s < 86400) return Math.floor(s/3600) + ' hr ago';
      var days = Math.floor(s/86400);
      return days + (days===1?' day ago':' days ago');
    }

    function wireQrow(container){
      container.querySelectorAll('.qrow').forEach(function(row){
        var id = row.getAttribute('data-id');
        var openBtn = row.querySelector('.js-open');
        var approveBtn = row.querySelector('.approve');
        if(openBtn){ openBtn.addEventListener('click', function(){ openDraft(id); }); }
        if(approveBtn){ approveBtn.addEventListener('click', function(){ approveDraft(id, row); }); }
      });
    }
    function wireRrow(container){
      container.querySelectorAll('.rrow').forEach(function(row){
        var id = row.getAttribute('data-id');
        row.style.cursor = 'pointer';
        row.addEventListener('click', function(){ openDraft(id); });
      });
    }
    function approveDraft(id, row){
      updateDraft(id, { status: 'sent', approvedAt: Date.now() });
      lastApprovedId = id;
      showToast('Approved.');
    }
    function openDraft(id){
      var d = findDraft(id);
      if(!d) return;
      currentDraftId = d.id;
      lastAIRequest = { page: d.type, userText: d.prompt || '' };
      var t = TYPE_META[d.type];
      if(t && t.page) goto(t.page);
      openAIModal();
      aiState.classList.add('hidden');
      aiBody.value = d.content || '';
      document.getElementById('ai-title').innerHTML = 'Edit <span class="it">' + escapeHTML(d.title || 'draft') + '</span>';
      document.getElementById('ai-sub').textContent = 'Changes save when you click "Save as draft" or "Approve & save".';
      aiUse.disabled = false; aiApprove.disabled = false; aiCopy.disabled = false; aiRegen.disabled = false;
    }

    // ===== AI (Groq) via Cloudflare Worker =====
    var aiModal = document.getElementById('ai-modal');
    var aiState = document.getElementById('ai-state');
    var aiStatus = document.getElementById('ai-status');
    var aiBody = document.getElementById('ai-body');
    var aiUse = document.getElementById('ai-use');
    var aiApprove = document.getElementById('ai-approve');
    var aiCopy = document.getElementById('ai-copy');
    var aiRegen = document.getElementById('ai-regen');
    var aiClose = document.getElementById('ai-close');
    var lastAIRequest = null;
    var currentDraftId = null;
    var lastApprovedId = null;

    function openAIModal(){ aiModal.classList.add('on'); }
    function closeAIModal(){ aiModal.classList.remove('on'); currentDraftId = null; }
    aiClose.addEventListener('click', closeAIModal);
    aiModal.addEventListener('click', function(e){ if(e.target === aiModal) closeAIModal(); });

    function setAILoading(msg){
      aiState.classList.remove('hidden');
      aiStatus.textContent = msg || 'Drafting with Atom…';
      aiBody.value = '';
      aiUse.disabled = true; aiApprove.disabled = true; aiCopy.disabled = true; aiRegen.disabled = true;
    }
    function setAIDone(content){
      aiState.classList.add('hidden');
      aiBody.value = content || '';
      aiUse.disabled = false; aiApprove.disabled = false; aiCopy.disabled = false; aiRegen.disabled = false;
    }
    function setAIError(msg){
      aiState.classList.remove('hidden');
      aiStatus.textContent = '';
      aiState.innerHTML = '<div style="color:var(--stamp);font-family:Inter,sans-serif;font-size:13.5px;">' + (msg || 'Something went wrong.') + '</div>';
      aiUse.disabled = true; aiApprove.disabled = true; aiCopy.disabled = true; aiRegen.disabled = false;
    }

    function systemPromptFor(page){
      var teacherCls = document.getElementById('ws-class-name').textContent || 'a class';
      var base = 'You are Atom, a drafting assistant for teachers. Draft a first version the teacher will edit. Be clear, warm, plain, no purple prose. Never claim to have final authority. The teacher is teaching: ' + teacherCls + '. Start the response with a short, plain title on the first line (no markdown, no quotes), then a blank line, then the body. ';
      var by = {
        assignment: 'Draft a printable worksheet. Include a title, numbered questions with point values in parentheses, and a mix of multiple choice and short answer as requested.',
        quiz: 'Draft a quiz with numbered questions, point values in parentheses, and an answer key at the end. Multiple choice options should be labeled 1-4.',
        rubric: 'Draft a rubric with rows and four levels (1 Beginning, 2 Developing, 3 Meeting, 4 Exceeding). Tie each row to a standard if given.',
        lesson: 'Draft a lesson plan with a warm up, mini lesson, guided practice, independent practice, and exit ticket. Include time budgets and materials.',
        passages: 'Draft a reading passage at the requested Lexile level with 3 to 5 comprehension questions after it.',
        slides: 'Draft an outline for a slide deck. One line per slide: title and one bullet.',
        docs: 'Draft the requested document in the teacher voice. Plain, warm, second person.',
        notes: 'Draft or improve a note home to a family. Warm, specific, not alarmed unless the situation warrants it.',
        diff: 'Adapt the assignment three ways: on grade, scaffolded, and ELL with sentence frames.'
      };
      return base + (by[page] || by.assignment);
    }

    async function callAI(page, userText){
      var email = getUserEmail();
      if(!email){
        setAIError('Please sign in with a .edu or .org email first.');
        openAIModal();
        return;
      }
      setAILoading('Drafting with Atom…');
      document.getElementById('ai-title').innerHTML = 'Your <span class="it">draft.</span>';
      document.getElementById('ai-sub').textContent = 'Edit anything before you save.';
      openAIModal();
      currentDraftId = null;
      var payload = {
        model: DEFAULT_MODEL,
        email: email,
        temperature: 0.5,
        max_tokens: 2048,
        messages: [
          { role: 'system', content: systemPromptFor(page) },
          { role: 'user', content: userText || 'Draft a first version.' }
        ]
      };
      lastAIRequest = { page: page, userText: userText };
      try {
        var res = await fetch(WORKER_URL + '/api/groq', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        var data = await res.json();
        if(!res.ok){
          setAIError((data && (data.error || data.detail)) || ('Error ' + res.status));
          return;
        }
        setAIDone((data && data.content) || '(empty response)');
      } catch(e){
        setAIError('Network error: ' + (e && e.message ? e.message : String(e)));
      }
    }

    aiCopy.addEventListener('click', function(){
      try { navigator.clipboard.writeText(aiBody.value || ''); showToast('Copied to clipboard.'); } catch(e){ showToast('Copy failed.'); }
    });
    function saveCurrentDraft(status){
      var content = aiBody.value || '';
      var title = titleFrom(content, lastAIRequest && lastAIRequest.userText);
      var teacherCls = document.getElementById('ws-class-name').textContent || '';
      if(currentDraftId){
        updateDraft(currentDraftId, { content: content, title: title, status: status, approvedAt: status === 'sent' ? Date.now() : null });
        lastApprovedId = status === 'sent' ? currentDraftId : lastApprovedId;
      } else {
        var id = addDraft({
          type: (lastAIRequest && lastAIRequest.page) || 'assignment',
          title: title, class: teacherCls, content: content,
          prompt: (lastAIRequest && lastAIRequest.userText) || '',
          status: status, approvedAt: status === 'sent' ? Date.now() : null
        });
        lastApprovedId = status === 'sent' ? id : lastApprovedId;
      }
    }
    aiUse.addEventListener('click', function(){
      saveCurrentDraft('awaiting');
      showToast('Draft saved to your queue.');
      closeAIModal();
    });
    aiApprove.addEventListener('click', function(){
      saveCurrentDraft('sent');
      showToast('Approved and saved.');
      closeAIModal();
    });
    aiRegen.addEventListener('click', function(){
      if(!lastAIRequest) return;
      callAI(lastAIRequest.page, lastAIRequest.userText);
    });

    // Ask box "Draft it" button, calls the Worker
    document.querySelectorAll('.ask-go').forEach(function(b){
      b.addEventListener('click', function(){
        var input = b.parentElement.querySelector('input');
        var text = input ? input.value.trim() : '';
        if(!text){ showToast('Type what you want to make first.'); return; }
        var page = b.closest('.ws-page');
        var pageKey = page ? page.getAttribute('data-page') : 'assignment';
        callAI(pageKey, text);
      });
    });

    // New draft menu
    var ndBtn = document.getElementById('new-draft-btn');
    var ndMenu = document.getElementById('new-menu');
    if(ndBtn && ndMenu){
      ndBtn.addEventListener('click', function(e){
        e.stopPropagation();
        ndMenu.classList.toggle('on');
      });
      ndMenu.querySelectorAll('a').forEach(function(a){
        a.addEventListener('click', function(){
          goto(a.getAttribute('data-nav'));
          ndMenu.classList.remove('on');
        });
      });
      document.addEventListener('click', function(e){
        if(!ndMenu.contains(e.target) && e.target !== ndBtn) ndMenu.classList.remove('on');
      });
    }

    // Sign out
    var soBtn = document.getElementById('signout');
    if(soBtn){
      soBtn.addEventListener('click', function(e){
        e.stopPropagation();
        if(!confirm('Sign out? Your local drafts stay on this device.')) return;
        try {
          localStorage.removeItem('atom-user');
          localStorage.removeItem('atom-email');
        } catch(e){}
        location.reload();
      });
    }

    // Static qrow/rrow wiring is not needed anymore, all rows are rendered by renderAll.

    // Class switcher toggle
    var clToggle = document.getElementById('ws-class-toggle');
    var clList = document.getElementById('class-list');
    if(clToggle && clList){
      clToggle.addEventListener('click', function(){
        clList.classList.toggle('on');
        clToggle.classList.toggle('open');
      });
      clList.querySelectorAll('.cl-row').forEach(function(r){
        r.addEventListener('click', function(e){
          e.stopPropagation();
          if(r.classList.contains('add')){ showToast('Add a class: coming soon.'); return; }
          clList.querySelectorAll('.cl-row').forEach(function(x){ x.classList.remove('on'); });
          r.classList.add('on');
          var b = r.querySelector('b'); var m = r.querySelector('.cl-m');
          if(b && m){
            document.getElementById('ws-class-name').textContent = m.textContent.trim();
            document.querySelector('.ws-class .cp').textContent = b.textContent;
          }
          clList.classList.remove('on');
          clToggle.classList.remove('open');
          showToast('Switched to ' + b.textContent + '.');
        });
      });
    }

    // Tool cards on Classes page
    document.querySelectorAll('.tool').forEach(function(t){
      if(!t.hasAttribute('data-goto')){
        t.style.cursor = 'pointer';
        t.addEventListener('click', function(){
          var name = t.querySelector('.tt');
          showToast('Opening ' + (name ? name.textContent : 'class') + '.');
        });
      }
    });

    // Regenerate / import mini buttons
    document.querySelectorAll('.mini-btn').forEach(function(b){
      b.addEventListener('click', function(){ showToast(b.textContent.trim() + ': running.'); });
    });

    // Settings save/cancel
    document.querySelectorAll('.sblock textarea, .frow input').forEach(function(el){
      // no-op, just to let them focus
    });
  })();
</script>
'''

HEAD = r'''<title>Atom Edu</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
'''

html = HEAD + STYLES + LANDING + MODAL + WORKSPACE + SCRIPT
html = html.replace('__LIGHT__', light_b64).replace('__DARK__', dark_b64)

with open('/tmp/atom/index.html','w') as f:
    f.write(html)
print("wrote", len(html), "bytes")
print("dashes:", sum(html.count(x) for x in ['—','–']))
