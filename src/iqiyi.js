// 爱奇艺 — AppleCMS -> NowShowTime JS 源 (generated, multi-runtime)
const BASE = "https://iqiyizyapi.com/api.php/provide/vod/";
const NAME = "爱奇艺";
const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';

function _h() { return { 'User-Agent': UA, 'Accept': 'application/json,text/plain,*/*' }; }
function _q(s) { return BASE + (BASE.indexOf('?') > -1 ? '&' : '?') + s; }

/* 把各种返回值统一成字符串 */
function _asText(r) {
  if (r === null || r === undefined) return '';
  if (typeof r === 'string') return r;
  if (typeof r === 'object') {
    if (typeof r.data === 'string') return r.data;
    if (typeof r.body === 'string') return r.body;
    if (typeof r.text === 'string') return r.text;
    if (r.data && typeof r.data.text === 'string') return r.data.text;
    if (r.data && typeof r.data.data === 'string') return r.data.data;
    try { return JSON.stringify(r); } catch (e) { return ''; }
  }
  return String(r);
}

/* 依次尝试运行时提供的 HTTP 能力，哪个先成功用哪个 */
async function _get(url) {
  var H = _h();
  var s = '';
  try {
    if (typeof $fetch !== 'undefined' && $fetch && typeof $fetch.get === 'function') {
      s = _asText(await $fetch.get(url, { headers: H, userAgent: UA })); if (s) return s;
    }
  } catch (e) {}
  try {
    if (typeof $http !== 'undefined' && $http && typeof $http.get === 'function') {
      s = _asText(await $http.get(url, { headers: H })); if (s) return s;
    }
  } catch (e) {}
  try {
    if (typeof req === 'function') { s = _asText(await req(url, { headers: H, method: 'GET' })); if (s) return s; }
  } catch (e) {}
  try {
    if (typeof request === 'function') { s = _asText(await request(url, { headers: H, method: 'GET' })); if (s) return s; }
  } catch (e) {}
  var objs = [];
  try { if (typeof http !== 'undefined') objs.push(http); } catch (e) {}
  try { if (typeof okhttp !== 'undefined') objs.push(okhttp); } catch (e) {}
  try { if (typeof $okhttp !== 'undefined') objs.push($okhttp); } catch (e) {}
  for (var i = 0; i < objs.length; i++) {
    try {
      if (objs[i] && typeof objs[i].get === 'function') {
        s = _asText(await objs[i].get(url, { headers: H })); if (s) return s;
      }
    } catch (e) {}
  }
  try {
    if (typeof fetch === 'function') {
      var r = await fetch(url, { headers: H });
      if (typeof r.text === 'function') { s = await r.text(); if (s) return s; }
    }
  } catch (e) {}
  return '';
}

function _j(t) {
  if (!t) return {};
  if (typeof t === 'object') return t;
  try { return JSON.parse(t); } catch (e) { return {}; }
}

var _cache = {};

function _map(list) {
  (list || []).forEach(function (v) { if (v && v.vod_play_url) _cache[String(v.vod_id)] = v; });
  return (list || []).map(function (v) {
    return {
      id: String(v.vod_id), title: v.vod_name || String(v.vod_id),
      cover: v.vod_pic || '', url: String(v.vod_id),
      description: v.vod_remarks || v.vod_year || '', createTime: Date.now()
    };
  });
}

var _cats = null;

async function getWebsiteInfo() {
  return { name: NAME, description: 'AppleCMS 采集源', icon: '', homepage: BASE };
}

async function getCategories() {
  if (_cats && _cats.length) return _cats;
  var j = _j(await _get(_q('ac=list')));
  var cls = (j.class || []).slice(0, 60).map(function (c) {
    return { id: String(c.type_id), name: c.type_name, ext: { url: _q('ac=detail&t=' + c.type_id + '&pg=1') } };
  });
  if (!cls.length) cls = [{ id: '1', name: '电影', ext: { url: _q('ac=detail&t=1&pg=1') } }];
  _cats = cls;
  return _cats;
}

function _ok(j) { return j && j.list && j.list.length; }

async function _list(q, fallback) {
  var j = _j(await _get(_q('ac=detail&' + q)));
  if (!_ok(j)) j = _j(await _get(_q('ac=list&' + q)));
  if (!_ok(j)) j = _j(await _get(_q('ac=videolist&' + q)));
  if (!_ok(j) && fallback) {
    j = _j(await _get(_q('ac=detail&' + fallback)));
    if (!_ok(j)) j = _j(await _get(_q('ac=list&' + fallback)));
  }
  return j;
}

async function getVideoList(page) {
  var j = await _list('pg=' + (page || 1));
  return _map(j.list);
}

async function getVideosByCategory(categoryId, page, sort) {
  var j = await _list('t=' + categoryId + '&pg=' + (page || 1), 'pg=' + (page || 1));
  return _map(j.list);
}

async function getPlayUrl(episodeUrl) {
  if (!episodeUrl) return '';
  if (/\.(m3u8?|mp4|flv)(\?|$)/i.test(episodeUrl)) return episodeUrl;
  try {
    var h = String(await _get(episodeUrl) || '');
    var m = h.match(/https?:\/\/[^\s"'\\<>]{6,240}?\.m3u8[^\s"'\\<>]{0,80}/);
    if (m) return m[0];
    var m2 = h.match(/src\s*=\s*["']([^"']+)/);
    if (m2 && /\.m3u8/.test(m2[1])) return m2[1];
  } catch (e) {}
  return episodeUrl;
}

async function getVideoDetail(videoId) {
  var v = _cache[String(videoId)] || {};
  if (!v.vod_play_url) {
    var j = _j(await _get(_q('ac=detail&ids=' + videoId)));
    v = (j.list || [])[0] || v;
  }
  var res = [];
  var lines = (v.vod_play_url || '').split('$$$');
  var eps = (lines[0] || '').split('#');
  eps.forEach(function (ep, i) {
    var p = ep.split('$');
    var nm = p.length > 1 ? p[0] : ('第' + (i + 1) + '集');
    var uu = p.length > 1 ? p[1] : p[0];
    if (uu && /^https?:\/\//.test(uu)) res.push({ id: String(i), name: nm, url: uu, size: '未知' });
  });
  if (!res.length && v.vod_play_url && /^https?:\/\//.test(v.vod_play_url))
    res = [{ id: '0', name: '播放', url: v.vod_play_url, size: '未知' }];
  return {
    id: String(videoId), title: v.vod_name || NAME, cover: v.vod_pic || '',
    description: String(v.vod_content || v.vod_blurb || '').replace(/<[^>]+>/g, '').slice(0, 400),
    resolutions: res
  };
}

async function search(keyword, page) {
  var j = _j(await _get(_q('ac=detail&wd=' + encodeURIComponent(keyword) + '&pg=' + (page || 1))));
  return _map(j.list);
}
