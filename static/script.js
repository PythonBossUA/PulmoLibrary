const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---- дата ---- */
const now = new Date();

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

/* ================= ФОРМУЛЯР ================= */
const form = document.getElementById('regForm');
const switchToLogin = document.getElementById('switchToLogin');
const switchToReg = document.getElementById('switchToReg');
const btnSubmit = document.getElementById('btnSubmit');
const formError = document.getElementById('formError');
const phoneInput = document.getElementById('fPhone');
const nameInput = document.getElementById('fName');
const regionSelect = document.getElementById('fRegion');
const villageInput = document.getElementById('fVillage');
const villageList = document.getElementById('villageList');
const passwordInput = document.getElementById('fPassword');

/* ---- валідатори ---- */
const NAME_RE = /^\p{L}{2,} \p{L}{2,}$/u;
function validateName(v){ return NAME_RE.test(v.trim()); }
function validatePassword(v){ return v.length >= 8; }
function validatePhone(v){
  const digits = v.replace(/\D/g, '');
  return digits.startsWith('38') && digits.length === 12;
}
function phoneToSend(v){
  const digits = v.replace(/\D/g, '');
  return digits.startsWith('38') ? digits.slice(2) : digits;
}

/* ---- допоміжні ---- */
function setError(msg){
  formError.textContent = msg || '';
  if(msg){ formError.classList.add('show'); }
  else { formError.classList.remove('show'); }
}
function setBusy(isBusy){
  btnSubmit.disabled = isBusy;
  btnSubmit.classList.toggle('busy', !!isBusy);
}
function flashError(fieldId){
  const fld = document.getElementById(fieldId);
  if(!fld) return;
  fld.classList.remove('err');
  void fld.offsetWidth;
  fld.classList.add('err');
}

/* ---- поетапне відкриття полів ---- */
let regionsLoaded = false;
let selectedSettlementId = null;

function lockField(id){
  const fld = document.getElementById(id);
  if(!fld) return;
  fld.classList.add('locked');
  const inputs = fld.querySelectorAll('input, select, button');
  inputs.forEach(el => el.disabled = true);
}
function unlockField(id){
  const fld = document.getElementById(id);
  if(!fld) return;
  fld.classList.remove('locked');
  const inputs = fld.querySelectorAll('input, select, button');
  inputs.forEach(el => el.disabled = false);
}

function resetRegion(){
  regionSelect.value = '';
}
function resetVillage(){
  villageInput.value = '';
  villageInput.dataset.settlementId = '';
  selectedSettlementId = null;
  hideVillageList();
}
function resetPhone(){
  phoneInput.value = '+38';
}
function resetPassword(){
  passwordInput.value = '';
}
function resetClub(){
  document.getElementById('fClub').checked = false;
}

function updateFieldLocks(){
  const nameOk = validateName(nameInput.value);
  const regionOk = !!regionSelect.value;
  const settlementOk = !!selectedSettlementId;
  const phoneOk = validatePhone(phoneInput.value.trim());
  const passwordOk = validatePassword(passwordInput.value);

  if(nameOk){
    unlockField('fldRegion');
    if(!regionsLoaded){
      loadRegions();
      regionsLoaded = true;
    }
  } else {
    lockField('fldRegion');
    resetRegion();
    regionsLoaded = false;
    lockField('fldVillage');
    resetVillage();
    lockField('fldPhone');
    resetPhone();
    lockField('fldPassword');
    resetPassword();
    lockField('fldClub');
    resetClub();
    lockField('fldSubmit');
    return;
  }

  if(regionOk){
    unlockField('fldVillage');
    document.getElementById('villageHint').textContent = 'введіть перші 2 літери назви';
  } else {
    lockField('fldVillage');
    resetVillage();
    lockField('fldPhone');
    resetPhone();
    lockField('fldPassword');
    resetPassword();
    lockField('fldClub');
    resetClub();
    lockField('fldSubmit');
    return;
  }

  if(settlementOk){
    unlockField('fldPhone');
  } else {
    lockField('fldPhone');
    resetPhone();
    lockField('fldPassword');
    resetPassword();
    lockField('fldClub');
    resetClub();
    lockField('fldSubmit');
    return;
  }

  if(phoneOk){
    unlockField('fldPassword');
  } else {
    lockField('fldPassword');
    resetPassword();
    lockField('fldClub');
    resetClub();
    lockField('fldSubmit');
    return;
  }

  if(passwordOk){
    unlockField('fldClub');
    unlockField('fldSubmit');
  } else {
    lockField('fldClub');
    resetClub();
    lockField('fldSubmit');
    return;
  }
}

/* ---- запит областей ---- */
async function loadRegions(){
  const hint = document.getElementById('regionHint');
  hint.textContent = 'завантаження областей…';
  try{
    const resp = await fetch('/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'need_regions' })
    });
    const data = await resp.json();
    if(data.type === 'regions_answer' && Array.isArray(data.regions)){
      regionSelect.innerHTML = '<option value="" disabled selected>Оберіть область</option>';
      data.regions.forEach(obj => {
        const [name, id] = Object.entries(obj)[0];
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = name;
        regionSelect.appendChild(opt);
      });
      hint.textContent = '27 областей';
    } else {
      hint.textContent = 'помилка завантаження областей';
    }
  }catch(e){
    hint.textContent = 'помилка зв’язку з сервером';
  }
}

/* ---- запит населених пунктів (з debounce 1с) ---- */
let villageTimer = null;
let villageAbort = null;

async function loadSettlements(startName){
  const regionId = regionSelect.value;
  if(!regionId) return;

  if(villageAbort) villageAbort.abort();
  villageAbort = new AbortController();

  const hint = document.getElementById('villageHint');
  hint.textContent = 'пошук населених пунктів…';
  hideVillageList();

  try{
    const resp = await fetch('/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'need_settlements',
        region_id: parseInt(regionId),
        settlement_startname: startName
      }),
      signal: villageAbort.signal
    });
    const data = await resp.json();
    if(data.type === 'settlements_answer' && Array.isArray(data.settlements)){
      if(data.settlements.length > 0){
        showVillageList(data.settlements);
        hint.textContent = 'оберіть зі списку';
      } else {
        hint.textContent = 'нічого не знайдено';
      }
    } else {
      hint.textContent = 'помилка пошуку';
    }
  }catch(e){
    if(e.name !== 'AbortError'){
      document.getElementById('villageHint').textContent = 'помилка зв’язку';
    }
  }
}

villageInput.addEventListener('input', function(){
  selectedSettlementId = null;
  this.dataset.settlementId = '';
  updateFieldLocks();

  clearTimeout(villageTimer);
  const v = this.value.trim();
  if(v.length < 2){
    hideVillageList();
    return;
  }
  villageTimer = setTimeout(() => {
    loadSettlements(v);
  }, 1000);
});

function showVillageList(settlements){
  villageList.innerHTML = '';
  settlements.forEach(obj => {
    const [name, id] = Object.entries(obj)[0];
    const item = document.createElement('div');
    item.className = 'autocomplete-item';
    item.textContent = name;
    item.dataset.id = id;
    item.addEventListener('mousedown', e => {
      e.preventDefault();
      villageInput.value = name;
      villageInput.dataset.settlementId = id;
      selectedSettlementId = id;
      hideVillageList();
      updateFieldLocks();
    });
    villageList.appendChild(item);
  });
  villageList.classList.add('show');
}

function hideVillageList(){
  villageList.classList.remove('show');
  villageList.innerHTML = '';
}

villageInput.addEventListener('blur', () => {
  setTimeout(hideVillageList, 200);
});

/* ---- обмеження вводу імені ---- */
nameInput.addEventListener('input', function(){
  let v = this.value;
  v = v.replace(/[^\p{L} ]/gu, '');
  if(v.startsWith(' ')) v = v.slice(1);
  const firstSpace = v.indexOf(' ');
  if(firstSpace !== -1){
    v = v.slice(0, firstSpace + 1) + v.slice(firstSpace + 1).replace(/ /g, '');
  }
  if(v.includes(' ')){
    const idx = v.indexOf(' ');
    if(idx < 2){
      v = v.slice(0, idx) + v.slice(idx + 1);
    }
  }
  this.value = v;
  updateFieldLocks();
});

/* ---- захист префіксу +38, перша цифра 0, максимум 10 цифр ---- */
phoneInput.addEventListener('input', function(){
  let v = this.value;
  if(!v.startsWith('+38')){
    const cleaned = v.replace(/^[+]?3?8?/, '');
    v = '+38' + cleaned;
  }
  const prefix = '+38';
  let digits = v.slice(prefix.length).replace(/\D/g, '');
  if(digits.length > 10){
    digits = digits.slice(0, 10);
  }
  if(digits.length > 0 && digits[0] !== '0'){
    digits = '0' + digits.slice(1);
  }
  this.value = prefix + digits;
  updateFieldLocks();
});

passwordInput.addEventListener('input', function(){
  updateFieldLocks();
});

regionSelect.addEventListener('change', function(){
  resetVillage();
  updateFieldLocks();
});

/* ---- перемикання форм ---- */
switchToLogin.addEventListener('click', ()=>{
  form.classList.add('login');
  setError('');
});
switchToReg.addEventListener('click', ()=>{
  form.classList.remove('login');
  setError('');
  document.getElementById('fName').focus();
});

/* ---- сабміт ---- */
form.addEventListener('submit', async e=>{
  e.preventDefault();
  setError('');
  const isLogin = form.classList.contains('login');

  if(isLogin){
    const loginName = document.getElementById('loginName');
    if(!loginName.value.trim()){
      flashError('fldLoginName');
      loginName.focus();
      return;
    }
    document.getElementById('rHello').textContent = 'З поверненням, ' + loginName.value.trim() + '!';
    document.getElementById('rTicket').style.display = 'none';
    document.getElementById('rDate').textContent = 'Дата входу: ' + now.toLocaleDateString('uk-UA',{day:'numeric',month:'long',year:'numeric'});
    document.getElementById('rStamp').textContent = 'Увійшли';
    document.getElementById('rHint').textContent = 'Обирайте книжку — тисніть на будь-який корінець нижче ↓';
    form.classList.add('done');
    return;
  }

  const name = nameInput.value.trim();
  const phone = phoneInput.value.trim();
  const password = passwordInput.value;
  const eventsOk = document.getElementById('fClub').checked;
  const regionId = regionSelect.value;
  const settlementId = selectedSettlementId;

  if(!validateName(name)){
    flashError('fldName');
    setError('Ім’я: мінімум 2 літери, один пробіл, мінімум 2 літери прізвища');
    nameInput.focus();
    return;
  }
  if(!regionId){
    flashError('fldRegion');
    setError('Оберіть область');
    return;
  }
  if(!settlementId){
    flashError('fldVillage');
    setError('Оберіть населений пункт зі списку');
    villageInput.focus();
    return;
  }
  if(!validatePhone(phone)){
    flashError('fldPhone');
    setError('Телефон: +38 і ще 10 цифр, перша — 0');
    phoneInput.focus();
    return;
  }
  if(!validatePassword(password)){
    flashError('fldPassword');
    setError('Пароль має містити щонайменше 8 символів');
    passwordInput.focus();
    return;
  }

  const payload = {
    type: 'registration',
    full_name: name,
    phone_number: phoneToSend(phone),
    password: password,
    events_ok: eventsOk,
    region_id: parseInt(regionId),
    settlement_id: parseInt(settlementId)
  };

  setBusy(true);
  try{
    const resp = await fetch('/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    let data = null;
    try{ data = await resp.json(); }catch(_){}

    if(data && data.type === 'success_create'){
      document.getElementById('rHello').textContent = 'Ласкаво просимо, ' + name + '!';
      document.getElementById('rTicket').style.display = '';
      document.getElementById('rNum').textContent = '№ ' + (1000 + Math.floor(Math.random()*9000));
      document.getElementById('rDate').textContent = 'Дата запису: ' + now.toLocaleDateString('uk-UA',{day:'numeric',month:'long',year:'numeric'});
      document.getElementById('rStamp').textContent = 'Зареєстровано';
      document.getElementById('rHint').textContent = 'Першу книжку обирайте просто зараз — тисніть на будь-який корінець нижче ↓';
      form.classList.add('done');
    }
    else if(data && data.type === 'bad_request'){
      const msg = data.detail || data.message || 'Некоректні дані запиту';
      setError(msg);
    }
    else{
      setError('Сталася невідома помилка сервера');
    }
  }catch(err){
    setError('Не вдалося зв’язатися з сервером. Перевірте з’єднання.');
  }finally{
    setBusy(false);
  }
});

/* ---- скидання форми ---- */
document.getElementById('btnAgain').addEventListener('click', ()=>{
  form.classList.remove('done');
  form.classList.remove('login');
  form.reset();
  phoneInput.value = '+38';
  selectedSettlementId = null;
  regionsLoaded = false;
  regionSelect.innerHTML = '<option value="" disabled selected>Оберіть область</option>';
  hideVillageList();
  setError('');
  updateFieldLocks();
  nameInput.focus();
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