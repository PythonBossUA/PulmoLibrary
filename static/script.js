const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---- дата ---- */
const now = new Date();
// document.getElementById('today').textContent =
//   'Сьогодні, ' + now.toLocaleDateString('uk-UA',{day:'numeric',month:'long'}) + ' · читальна зала: вівт–суб 10:00–18:00';
// document.getElementById('year').textContent = now.getFullYear();

/* ---- слово з корінців ---- */
const WORD = 'БІБЛІОТЕКА'.split('');
const PAL = ['#8a3b2d','#b3762c','#57684a','#3e5a6e','#7c4a67','#a8552f','#4e4a72','#8f8036','#6d3f34','#43604f','#9c3a3a','#c08a2d','#5d5648'];
const shelfEl = document.getElementById('titleShelf');
WORD.forEach((ch,i)=>{
  const d = document.createElement('div');
  d.className = 'tsp';
  d.style.setProperty('--i', i);
  d.style.setProperty('--r', ((i*53)%5-2)+'deg');
  d.style.background = PAL[i % PAL.length];
  d.textContent = ch;
  shelfEl.appendChild(d);
});
const gap = document.createElement('div');
gap.className = 'tsp out'; gap.style.setProperty('--i', WORD.length);
gap.textContent = ''; gap.title = 'ця книжка зараз у читачів';
shelfEl.appendChild(gap);

/* ---- міні-корінці в 3д сцені ---- */
const ss = document.getElementById('sceneSpines');
for(let i=0;i<9;i++){
  const b = document.createElement('i');
  b.style.height = (42 + (i*29)%46) + 'px';
  b.style.width = (14 + (i*7)%10) + 'px';
  b.style.background = PAL[(i*3+2) % PAL.length];
  ss.appendChild(b);
}

/* ---- каталог: дані 33 літер ---- */
const BOOKS = [
 {l:'А', t:'«Аліса в Країні Чудес»', a:'Льюїс Керрол', ok:true},
 {l:'Б', t:'«Байки»', a:'Леонід Глібов', ok:true},
 {l:'В', t:'«Вечори на хуторі біля Диканьки»', a:'Микола Гоголь', ok:false, due:'до 21 травня'},
 {l:'Г', t:'«Гайдамаки»', a:'Тарас Шевченко', ok:true},
 {l:'Ґ', t:'«Ґоверла. Легенди гір»', a:'збірка карпатських оповідей', ok:true},
 {l:'Д', t:'«Диво»', a:'Павло Загребельний', ok:true},
 {l:'Е', t:'«Енеїда»', a:'Іван Котляревський', ok:true},
 {l:'Є', t:'«Євшан-зілля»', a:'Володимир Бєляєв', ok:false, due:'до 3 червня'},
 {l:'Ж', t:'«Жовтий князь»', a:'Василь Барка', ok:true},
 {l:'З', t:'«Земля»', a:'Ольга Кобилянська', ok:true},
 {l:'И', special:'Літера «И» майже не починає слів — тому цей корінець стоїть для прикраси. Спитайте бібліотекарку: вона знає все.'},
 {l:'І', t:'«Інтернат»', a:'Сергій Жадан', ok:true},
 {l:'Ї', t:'«Їжачок у тумані»', a:'казка-картинка для вечорів', ok:true},
 {l:'Й', t:'«Фауст»', a:'Й.-В. Ґете, переклад М. Лукаша', ok:true},
 {l:'К', t:'«Кайдашева сім’я»', a:'Іван Нечуй-Левицький', ok:true},
 {l:'Л', t:'«Лісова пісня»', a:'Леся Українка', ok:true},
 {l:'М', t:'«Місто»', a:'Валер’ян Підмогильний', ok:true},
 {l:'Н', t:'«Наталка Полтавка»', a:'Іван Котляревський', ok:true},
 {l:'О', t:'«Овід»', a:'Етель Ліліан Войніч', ok:false, due:'до 17 травня'},
 {l:'П', t:'«Перехресні стежки»', a:'Іван Франко', ok:true},
 {l:'Р', t:'«Роксолана»', a:'Павло Загребельний', ok:true},
 {l:'С', t:'«Собор»', a:'Олесь Гончар', ok:true},
 {l:'Т', t:'«Тіні забутих предків»', a:'Михайло Коцюбинський', ok:true},
 {l:'У', t:'«Українські народні казки»', a:'збірка, читана вголос сотні разів', ok:true},
 {l:'Ф', t:'«Фарбований лис»', a:'Іван Франко', ok:true},
 {l:'Х', t:'«Хіба ревуть воли, як ясла повні?»', a:'Панас Мирний', ok:true},
 {l:'Ц', t:'«Циганка Аза»', a:'Михайло Старицький', ok:true},
 {l:'Ч', t:'«Чорна рада»', a:'Пантелеймон Куліш', ok:true},
 {l:'Ш', t:'«Кобзар»', a:'Тарас Шевченко', ok:true, note:'той самий, що в читачів 😉'},
 {l:'Щ', t:'«Щедрівки та засівалки»', a:'збірка до зимових свят', ok:true},
 {l:'Ь', special:'З «ь» не починається жодне слово — він лише підтримує інших іззаду. За це ми його й любимо.'},
 {l:'Ю', t:'«Юність наших дідів»', a:'Роман Іваничук', ok:false, due:'до 29 травня'},
 {l:'Я', t:'«Я (Романтика)»', a:'Микола Хвильовий', ok:true}
];
const NOTES = {
 'А':'переклад старенький, але пахне як новий',
 'Е':'читайте вголос — Котляревський це любить',
 'К':'питайте також продовження, воно в шухлядці',
 'Л':'до прем’єри в клубі розібрали за день',
 'С':'три примірники, бо один — «для розмов»',
 'Т':'найкраще читати восени, біля вікна',
 'У':'читана вголос сотні разів — і ще почитаємо',
 'Ш':'той самий, що в читачів 😉'
};
const rowA = document.getElementById('rowA'), rowB = document.getElementById('rowB');
const spineEls = [];
BOOKS.forEach((d,i)=>{
  const b = document.createElement('button');
  b.type='button'; b.className='spine';
  b.style.height = (128 + (i*47)%76) + 'px';
  b.style.width  = (34 + (i*11)%15) + 'px';
  b.style.setProperty('--r', ((i*37)%5-2)+'deg');
  if(i%8===5){ b.classList.add('paper'); b.style.background='#e7d7ae'; }
  else b.style.background = PAL[i % PAL.length];
  if(d.special) b.classList.add('special');
  b.title = d.special ? (d.l+' — особливий корінець') : (d.l+' — '+d.t);
  b.setAttribute('aria-label', b.title);
  b.innerHTML = `<span class="lt">${d.l}</span><span class="ribs"></span>`;
  b.addEventListener('click', ()=>select(i));
  (i < 19 ? rowA : rowB).appendChild(b);
  spineEls.push(b);
});
/* реквізит на полиці */
const props = document.createElement('div');
props.className='shelf-props'; props.setAttribute('aria-hidden','true');
props.innerHTML='🪴'; rowB.appendChild(props);

const card = document.getElementById('catalog-card');
function select(i){
  spineEls.forEach(s=>s.classList.remove('active'));
  spineEls[i].classList.add('active');
  const d = BOOKS[i];
  document.getElementById('ccLetter').textContent = d.l;
  document.getElementById('ccKicker').textContent = d.l;
  const stamp = document.getElementById('ccStamp');
  const note = document.getElementById('ccNote');
  if(d.special){
    document.getElementById('ccTitle').textContent = 'Особлива поличка';
    document.getElementById('ccAuthor').textContent = '';
    note.textContent = d.special;
    stamp.className='stamp rare'; stamp.textContent='рідкісний';
  } else {
    document.getElementById('ccTitle').textContent = d.t;
    document.getElementById('ccAuthor').textContent = d.a;
    note.textContent = NOTES[d.l] || (d.ok ? '' : 'дуже просили повернути акуратно');
    if(d.ok){ stamp.className='stamp ok'; stamp.textContent='у залі'; }
    else { stamp.className='stamp away'; stamp.textContent='читається ' + d.due; }
  }
  document.getElementById('ccPlace').textContent =
    d.special ? 'під склом · запитайте бібліотекарку'
    : `зала ${(i%2)+1} · полиця ${(i%5)+1} · ${d.ok ? 'можна брати сьогодні' : 'запишемо вас у чергу'}`;
  card.classList.remove('pop'); void card.offsetWidth; card.classList.add('pop');
}
/* пошук літерою */
document.getElementById('letterSearch').addEventListener('input', e=>{
  const v = e.target.value.trim().toUpperCase();
  if(!v) return;
  const i = BOOKS.findIndex(d=>d.l===v);
  if(i>-1){ select(i); spineEls[i].scrollIntoView({block:'nearest', inline:'center', behavior: RM?'auto':'smooth'}); }
});

/* ---- формуляр ---- */
const form = document.getElementById('regForm');
form.addEventListener('submit', e=>{
  e.preventDefault();
  const name = document.getElementById('fName');
  const fld = document.getElementById('fldName');
  if(!name.value.trim()){ fld.classList.remove('err'); void fld.offsetWidth; fld.classList.add('err'); name.focus(); return; }
  document.getElementById('rHello').textContent = 'Ласкаво просимо, ' + name.value.trim() + '!';
  document.getElementById('rNum').textContent = '№ ' + (1000 + Math.floor(Math.random()*9000));
  document.getElementById('rDate').textContent = 'Дата запису: ' + now.toLocaleDateString('uk-UA',{day:'numeric',month:'long',year:'numeric'});
  form.classList.add('done');
});
document.getElementById('btnAgain').addEventListener('click', ()=>{
  form.classList.remove('done'); form.reset();
  document.getElementById('fName').focus();
});

/* ---- лічильники ---- */
document.getElementById('stYears').dataset.count = now.getFullYear() - 1948;
function count(el){
  const target = +el.dataset.count;
  if(RM){ el.textContent = target.toLocaleString('uk-UA'); return; }
  const t0 = performance.now(), dur = 1400;
  (function tick(t){
    const p = Math.min((t-t0)/dur, 1), ease = 1-Math.pow(1-p,3);
    el.textContent = Math.round(target*ease).toLocaleString('uk-UA');
    if(p<1) requestAnimationFrame(tick);
  })(t0);
}
let counted=false;
new IntersectionObserver(es=>{
  es.forEach(en=>{ if(en.isIntersecting && !counted){ counted=true;
    document.querySelectorAll('#stats b').forEach(count); }});
},{threshold:.3}).observe(document.getElementById('stats'));

/* ---- поява при скролі ---- */
const revs = document.querySelectorAll('.rev');
if(RM){ revs.forEach(r=>r.classList.add('in')); }
else{
  const io = new IntersectionObserver(es=>{
    es.forEach(en=>{ if(en.isIntersecting){ en.target.classList.add('in'); io.unobserve(en.target); }});
  },{threshold:.12});
  revs.forEach(r=>io.observe(r));
}