const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
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

/* ---- каталог ---- */
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
document.getElementById('letterSearch').addEventListener('input', e=>{
  const v = e.target.value.trim().toUpperCase();
  if(!v) return;
  const i = BOOKS.findIndex(d=>d.l===v);
  if(i>-1){ select(i); spineEls[i].scrollIntoView({block:'nearest', inline:'center', behavior: RM?'auto':'smooth'}); }
});

/* ================= JWT ================= */
const TOKEN_KEY = 'library_jwt';
let expiryTimer = null;

function decodeJwt(token){
  try{
    const parts = token.split('.');
    if(parts.length !== 3) return null;
    const b64 = parts[1].replace(/-/g,'+').replace(/_/g,'/');
    const pad = b64.length % 4 === 0 ? '' : '='.repeat(4 - (b64.length % 4));
    return JSON.parse(atob(b64 + pad));
  }catch(e){ return null; }
}

function isTokenValid(){
  const token = getToken();
  if(!token) return false;
  const payload = decodeJwt(token);
  if(!payload || !payload.exp) return false;
  return payload.exp > Math.floor(Date.now() / 1000);
}

function saveToken(jwt){
  localStorage.setItem(TOKEN_KEY, jwt);
  scheduleTokenExpiry();
  updateUserWidget();
  checkAuthState();
}
function getToken(){
  return localStorage.getItem(TOKEN_KEY);
}
function removeToken(){
  localStorage.removeItem(TOKEN_KEY);
  if(expiryTimer){ clearTimeout(expiryTimer); expiryTimer = null; }
  updateUserWidget();
  checkAuthState();
}
function scheduleTokenExpiry(){
  if(expiryTimer){ clearTimeout(expiryTimer); expiryTimer = null; }
  const token = getToken();
  if(!token) return;
  const payload = decodeJwt(token);
  if(!payload || !payload.exp) return;
  const nowSec = Math.floor(Date.now() / 1000);
  const remaining = payload.exp - nowSec;
  if(remaining <= 0){ removeToken(); return; }
  expiryTimer = setTimeout(removeToken, remaining * 1000);
}

function apiFetch(payload){
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if(token) headers['Authorization'] = 'Bearer ' + token;
  return fetch('/events', {
    method: 'POST',
    headers,
    body: JSON.stringify(payload)
  });
}

/* ================= ВІДЖЕТ КОРИСТУВАЧА ================= */
const userWidget = document.getElementById('userWidget');
const userBtn = document.getElementById('userBtn');
const userNameEl = document.getElementById('userName');

function updateUserWidget(){
  const token = getToken();
  if(!token){
    userWidget.hidden = true;
    return;
  }
  const payload = decodeJwt(token);
  if(!payload){
    removeToken();
    return;
  }
  const displayName = [payload.first_name, payload.last_name].filter(Boolean).join(' ');
  userNameEl.textContent = displayName.trim();
  userWidget.hidden = false;
}

userBtn.addEventListener('click', ()=>{
  openProfileModal();
});

/* ================= ПРОФІЛЬ ================= */
const profileModal = document.getElementById('profileModal');
const profileBackdrop = document.getElementById('profileBackdrop');
const profileClose = document.getElementById('profileClose');
const btnLogout = document.getElementById('btnLogout');

function openProfileModal(){
  const token = getToken();
  if(!token) return;
  const p = decodeJwt(token);
  if(!p) return;

  document.getElementById('profileTitle').textContent =
    [p.first_name, p.last_name].filter(Boolean).join(' ');
  document.getElementById('profilePhone').textContent = p.phone_number || '—';
  document.getElementById('profileRegion').textContent = p.region || '—';
  document.getElementById('profileSettlement').textContent = p.settlement || '—';
  document.getElementById('profileEvents').textContent = p.events_ok ? 'Так ✓' : 'Ні';

  profileModal.hidden = false;
  document.body.style.overflow = 'hidden';
}
function closeProfileModal(){
  profileModal.hidden = true;
  document.body.style.overflow = '';
}

profileClose.addEventListener('click', closeProfileModal);
profileBackdrop.addEventListener('click', closeProfileModal);
document.addEventListener('keydown', e=>{
  if(e.key === 'Escape' && !profileModal.hidden) closeProfileModal();
});

btnLogout.addEventListener('click', ()=>{
  removeToken();
  closeProfileModal();
  form.classList.remove('done');
  form.classList.remove('login');
  resetRegistrationForm();
  updateFieldLocks();
});

/* ================= БЛОКУВАННЯ ФОРМИ ПРИ ТОКЕНІ ================= */
function checkAuthState(){
  if(isTokenValid() && !form.classList.contains('done')){
    form.classList.add('authorized');
  } else {
    form.classList.remove('authorized');
  }
}

/* ================= ФОРМУЛЯР ================= */
const form = document.getElementById('regForm');
const switchToLogin = document.getElementById('switchToLogin');
const switchToReg = document.getElementById('switchToReg');
const btnSubmit = document.getElementById('btnSubmit');
const formError = document.getElementById('formError');
const phoneInput = document.getElementById('fPhone');
const regionSelect = document.getElementById('fRegion');
const villageInput = document.getElementById('fVillage');
const villageList = document.getElementById('villageList');
const passwordInput = document.getElementById('fPassword');

const firstNameInput = document.getElementById('fFirstName');
const lastNameInput = document.getElementById('fLastName');
const surnameInput = document.getElementById('fSurname');

/* ---- поля логіну ---- */
const loginFirstNameInput = document.getElementById('loginFirstName');
const loginLastNameInput = document.getElementById('loginLastName');
const loginSurnameInput = document.getElementById('loginSurname');
const loginRegionSelect = document.getElementById('loginRegion');
const loginVillageInput = document.getElementById('loginVillage');
const loginVillageList = document.getElementById('loginVillageList');
const loginPasswordInput = document.getElementById('loginPassword');
const btnLogin = document.getElementById('btnLogin');

/* ---- валідатори ---- */
const SINGLE_NAME_RE = /^\p{L}{2,}$/u;
function validateSingleName(v){ return SINGLE_NAME_RE.test(v.trim()); }
function validateOptionalName(v){
  const t = v.trim();
  if(!t) return true;
  return SINGLE_NAME_RE.test(t);
}
function validatePassword(v){ return v.length >= 8; }
function validatePhone(v){
  const digits = v.replace(/\D/g, '');
  return digits.startsWith('38') && digits.length === 12;
}
function phoneToSend(v){
  const digits = v.replace(/\D/g, '');
  return digits.startsWith('38') ? digits.slice(2) : digits;
}
function sanitizeName(v){
  return v.replace(/[^\p{L}]/gu, '');
}

/* ---- допоміжні ---- */
function setError(msg){
  formError.textContent = msg || '';
  if(msg){ formError.classList.add('show'); }
  else { formError.classList.remove('show'); }
}
function setBusy(btn, isBusy){
  btn.disabled = isBusy;
  btn.classList.toggle('busy', !!isBusy);
}
function flashError(fieldId){
  const fld = document.getElementById(fieldId);
  if(!fld) return;
  fld.classList.remove('err');
  void fld.offsetWidth;
  fld.classList.add('err');
}

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

/* ================= ОБЛАСТІ (кеш) ================= */
let cachedRegions = null;

async function fetchRegions(){
  if(cachedRegions) return cachedRegions;
  const resp = await apiFetch({ type: 'need_regions' });
  const data = await resp.json();
  if(data.type === 'regions_answer' && Array.isArray(data.regions)){
    cachedRegions = data.regions;
  }
  return cachedRegions;
}

async function fillRegionSelect(selectEl, hintEl){
  if(hintEl) hintEl.textContent = 'завантаження областей…';
  try{
    const regions = await fetchRegions();
    if(!regions){
      if(hintEl) hintEl.textContent = 'помилка завантаження';
      return;
    }
    selectEl.innerHTML = '<option value="" disabled selected>Оберіть область</option>';
    regions.forEach(obj => {
      const [name, id] = Object.entries(obj)[0];
      const opt = document.createElement('option');
      opt.value = id;
      opt.textContent = name;
      selectEl.appendChild(opt);
    });
    if(hintEl) hintEl.textContent = '27 областей';
  }catch(e){
    if(hintEl) hintEl.textContent = 'помилка зв’язку';
  }
}

/* ================= ПОЕТАПНЕ ВІДКРИТТЯ (РЕЄСТРАЦІЯ) ================= */
let regionsLoadedReg = false;
let selectedSettlementId = null;

function resetRegistrationForm(){
  firstNameInput.value = '';
  lastNameInput.value = '';
  surnameInput.value = '';
  regionSelect.innerHTML = '<option value="" disabled selected>Оберіть область</option>';
  villageInput.value = '';
  villageInput.dataset.settlementId = '';
  selectedSettlementId = null;
  hideVillageList(villageList);
  phoneInput.value = '+38';
  passwordInput.value = '';
  document.getElementById('fClub').checked = false;
  regionsLoadedReg = false;
}

function updateFieldLocks(){
  const firstOk = validateSingleName(firstNameInput.value);
  const lastOk = validateSingleName(lastNameInput.value);
  const surnameOk = validateOptionalName(surnameInput.value);
  const regionOk = !!regionSelect.value;
  const settlementOk = !!selectedSettlementId;
  const phoneOk = validatePhone(phoneInput.value.trim());
  const passwordOk = validatePassword(passwordInput.value);

  if(firstOk){
    unlockField('fldLastName');
  } else {
    lockField('fldLastName');
    lockField('fldSurname');
    lockField('fldRegion');
    lockField('fldVillage');
    lockField('fldPhone');
    lockField('fldPassword');
    lockField('fldClub');
    lockField('fldSubmit');
    return;
  }

  if(lastOk){
    unlockField('fldSurname');
    unlockField('fldRegion');
    if(!regionsLoadedReg){
      fillRegionSelect(regionSelect, document.getElementById('regionHint'));
      regionsLoadedReg = true;
    }
  } else {
    lockField('fldSurname');
    lockField('fldRegion');
    lockField('fldVillage');
    lockField('fldPhone');
    lockField('fldPassword');
    lockField('fldClub');
    lockField('fldSubmit');
    return;
  }

  if(regionOk){
    unlockField('fldVillage');
    document.getElementById('villageHint').textContent = 'введіть перші 2 літери назви';
  } else {
    lockField('fldVillage');
    lockField('fldPhone');
    lockField('fldPassword');
    lockField('fldClub');
    lockField('fldSubmit');
    return;
  }

  if(settlementOk){
    unlockField('fldPhone');
  } else {
    lockField('fldPhone');
    lockField('fldPassword');
    lockField('fldClub');
    lockField('fldSubmit');
    return;
  }

  if(phoneOk){
    unlockField('fldPassword');
  } else {
    lockField('fldPassword');
    lockField('fldClub');
    lockField('fldSubmit');
    return;
  }

  if(passwordOk){
    unlockField('fldClub');
    unlockField('fldSubmit');
  } else {
    lockField('fldClub');
    lockField('fldSubmit');
    return;
  }
}

/* ================= НАСЕЛЕНІ ПУНКТИ ================= */
let villageTimer = null;
let villageAbort = null;

async function loadSettlements(regionId, startName, listEl, hintEl){
  if(villageAbort) villageAbort.abort();
  villageAbort = new AbortController();

  if(hintEl) hintEl.textContent = 'пошук населених пунктів…';
  hideVillageList(listEl);

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
        showVillageList(data.settlements, listEl);
        if(hintEl) hintEl.textContent = 'оберіть зі списку';
      } else {
        if(hintEl) hintEl.textContent = 'нічого не знайдено';
      }
    } else {
      if(hintEl) hintEl.textContent = 'помилка пошуку';
    }
  }catch(e){
    if(e.name !== 'AbortError' && hintEl){
      hintEl.textContent = 'помилка зв’язку';
    }
  }
}

function showVillageList(settlements, listEl){
  listEl.innerHTML = '';
  settlements.forEach(obj => {
    const [name, id] = Object.entries(obj)[0];
    const item = document.createElement('div');
    item.className = 'autocomplete-item';
    item.textContent = name;
    item.dataset.id = id;
    item.addEventListener('mousedown', e => {
      e.preventDefault();
      const input = listEl.closest('.autocomplete-wrap').querySelector('input');
      input.value = name;
      input.dataset.settlementId = id;
      if(listEl === villageList){
        selectedSettlementId = id;
        updateFieldLocks();
      } else {
        selectedLoginSettlementId = id;
        updateLoginFieldLocks();
      }
      hideVillageList(listEl);
    });
    listEl.appendChild(item);
  });
  listEl.classList.add('show');
}

function hideVillageList(listEl){
  listEl.classList.remove('show');
  listEl.innerHTML = '';
}

villageInput.addEventListener('input', function(){
  selectedSettlementId = null;
  this.dataset.settlementId = '';
  updateFieldLocks();
  clearTimeout(villageTimer);
  const v = this.value.trim();
  if(v.length < 2){
    hideVillageList(villageList);
    return;
  }
  villageTimer = setTimeout(() => {
    loadSettlements(regionSelect.value, v, villageList, document.getElementById('villageHint'));
  }, 1000);
});

villageInput.addEventListener('blur', () => {
  setTimeout(()=>hideVillageList(villageList), 200);
});

/* ---- обмеження вводу імен ---- */
firstNameInput.addEventListener('input', function(){
  this.value = sanitizeName(this.value);
  updateFieldLocks();
});
lastNameInput.addEventListener('input', function(){
  this.value = sanitizeName(this.value);
  updateFieldLocks();
});
surnameInput.addEventListener('input', function(){
  this.value = sanitizeName(this.value);
  updateFieldLocks();
});

/* ---- телефон ---- */
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
  selectedSettlementId = null;
  villageInput.value = '';
  villageInput.dataset.settlementId = '';
  hideVillageList(villageList);
  updateFieldLocks();
});

/* ================= ПОЕТАПНЕ ВІДКРИТТЯ (ЛОГІН) ================= */
let regionsLoadedLogin = false;
let selectedLoginSettlementId = null;
let loginVillageTimer = null;

function updateLoginFieldLocks(){
  const firstOk = validateSingleName(loginFirstNameInput.value);
  const lastOk = validateSingleName(loginLastNameInput.value);
  const regionOk = !!loginRegionSelect.value;
  const settlementOk = !!selectedLoginSettlementId;
  const passwordOk = validatePassword(loginPasswordInput.value);

  if(firstOk){
    unlockField('fldLoginLastName');
  } else {
    lockField('fldLoginLastName');
    lockField('fldLoginSurname');
    lockField('fldLoginRegion');
    lockField('fldLoginVillage');
    lockField('fldLoginPassword');
    btnLogin.disabled = true;
    return;
  }

  if(lastOk){
    unlockField('fldLoginSurname');
    unlockField('fldLoginRegion');
    if(!regionsLoadedLogin){
      fillRegionSelect(loginRegionSelect, document.getElementById('loginRegionHint'));
      regionsLoadedLogin = true;
    }
  } else {
    lockField('fldLoginSurname');
    lockField('fldLoginRegion');
    lockField('fldLoginVillage');
    lockField('fldLoginPassword');
    btnLogin.disabled = true;
    return;
  }

  if(regionOk){
    unlockField('fldLoginVillage');
    document.getElementById('loginVillageHint').textContent = 'введіть перші 2 літери назви';
  } else {
    lockField('fldLoginVillage');
    lockField('fldLoginPassword');
    btnLogin.disabled = true;
    return;
  }

  if(settlementOk){
    unlockField('fldLoginPassword');
  } else {
    lockField('fldLoginPassword');
    btnLogin.disabled = true;
    return;
  }

  if(passwordOk){
    btnLogin.disabled = false;
  } else {
    btnLogin.disabled = true;
  }
}

loginFirstNameInput.addEventListener('input', function(){
  this.value = sanitizeName(this.value);
  updateLoginFieldLocks();
});
loginLastNameInput.addEventListener('input', function(){
  this.value = sanitizeName(this.value);
  updateLoginFieldLocks();
});
loginSurnameInput.addEventListener('input', function(){
  this.value = sanitizeName(this.value);
  updateLoginFieldLocks();
});

loginRegionSelect.addEventListener('change', function(){
  selectedLoginSettlementId = null;
  loginVillageInput.value = '';
  loginVillageInput.dataset.settlementId = '';
  hideVillageList(loginVillageList);
  updateLoginFieldLocks();
});

loginVillageInput.addEventListener('input', function(){
  selectedLoginSettlementId = null;
  this.dataset.settlementId = '';
  updateLoginFieldLocks();
  clearTimeout(loginVillageTimer);
  const v = this.value.trim();
  if(v.length < 2){
    hideVillageList(loginVillageList);
    return;
  }
  loginVillageTimer = setTimeout(() => {
    loadSettlements(loginRegionSelect.value, v, loginVillageList, document.getElementById('loginVillageHint'));
  }, 1000);
});

loginVillageInput.addEventListener('blur', () => {
  setTimeout(()=>hideVillageList(loginVillageList), 200);
});

loginPasswordInput.addEventListener('input', function(){
  updateLoginFieldLocks();
});

/* ================= ПЕРЕМИКАННЯ ФОРМ ================= */
switchToLogin.addEventListener('click', ()=>{
  form.classList.add('login');
  setError('');
  updateLoginFieldLocks();
});
switchToReg.addEventListener('click', ()=>{
  form.classList.remove('login');
  setError('');
  updateFieldLocks();
  firstNameInput.focus();
});

/* ================= САБМІТ ================= */
form.addEventListener('submit', async e=>{
  e.preventDefault();
  setError('');
  const isLogin = form.classList.contains('login');

  if(isLogin){
    const firstName = loginFirstNameInput.value.trim();
    const lastName = loginLastNameInput.value.trim();
    const surname = loginSurnameInput.value.trim();
    const regionId = loginRegionSelect.value;
    const settlementId = selectedLoginSettlementId;
    const password = loginPasswordInput.value;

    if(!validateSingleName(firstName)){
      flashError('fldLoginFirstName');
      setError('Ім’я: мінімум 2 літери');
      loginFirstNameInput.focus();
      return;
    }
    if(!validateSingleName(lastName)){
      flashError('fldLoginLastName');
      setError('Прізвище: мінімум 2 літери');
      loginLastNameInput.focus();
      return;
    }
    if(!validateOptionalName(surname)){
      flashError('fldLoginSurname');
      setError('По батькові: мінімум 2 літери');
      loginSurnameInput.focus();
      return;
    }
    if(!regionId){
      flashError('fldLoginRegion');
      setError('Оберіть область');
      return;
    }
    if(!settlementId){
      flashError('fldLoginVillage');
      setError('Оберіть населений пункт зі списку');
      loginVillageInput.focus();
      return;
    }
    if(!validatePassword(password)){
      flashError('fldLoginPassword');
      setError('Пароль має містити щонайменше 8 символів');
      loginPasswordInput.focus();
      return;
    }

    const payload = {
      type: 'auth',
      first_name: firstName,
      last_name: lastName,
      surname: surname,
      region_id: parseInt(regionId),
      settlement_id: parseInt(settlementId),
      password: password
    };

    setBusy(btnLogin, true);
    try{
      const resp = await apiFetch(payload);
      let data = null;
      try{ data = await resp.json(); }catch(_){}

      if(data && data.type === 'success_auth' && data.jwt){
        saveToken(data.jwt);
        document.getElementById('rHello').textContent = 'З поверненням, ' + firstName + ' ' + lastName + '!';
        document.getElementById('rStamp').textContent = 'Увійшли';
        document.getElementById('rHint').textContent = 'Ви успішно авторизувались на сайті 😊';
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
      setBusy(btnLogin, false);
    }
    return;
  }

  /* --- реєстрація --- */
  const firstName = firstNameInput.value.trim();
  const lastName = lastNameInput.value.trim();
  const surname = surnameInput.value.trim();
  const phone = phoneInput.value.trim();
  const password = passwordInput.value;
  const eventsOk = document.getElementById('fClub').checked;
  const regionId = regionSelect.value;
  const settlementId = selectedSettlementId;

  if(!validateSingleName(firstName)){
    flashError('fldFirstName');
    setError('Ім’я: мінімум 2 літери');
    firstNameInput.focus();
    return;
  }
  if(!validateSingleName(lastName)){
    flashError('fldLastName');
    setError('Прізвище: мінімум 2 літери');
    lastNameInput.focus();
    return;
  }
  if(!validateOptionalName(surname)){
    flashError('fldSurname');
    setError('По батькові: мінімум 2 літери');
    surnameInput.focus();
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
    first_name: firstName,
    last_name: lastName,
    surname: surname,
    phone_number: phoneToSend(phone),
    password: password,
    events_ok: eventsOk,
    region_id: parseInt(regionId),
    settlement_id: parseInt(settlementId)
  };

  setBusy(btnSubmit, true);
  try{
    const resp = await apiFetch(payload);
    let data = null;
    try{ data = await resp.json(); }catch(_){}

    if(data && data.type === 'success_create' && data.jwt){
      saveToken(data.jwt);
      document.getElementById('rHello').textContent = 'Ласкаво просимо, ' + firstName + ' ' + lastName + '!';
      document.getElementById('rStamp').textContent = 'Зареєстровано';
      document.getElementById('rHint').textContent = 'Ви успішно авторизувались на сайті 😊';
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
    setBusy(btnSubmit, false);
  }
});

/* ================= ІНІЦІАЛІЗАЦІЯ ================= */
updateUserWidget();
scheduleTokenExpiry();
checkAuthState();
updateFieldLocks();

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