#!/usr/bin/env python3
# 生成 映盒(NowShowTime) JS 订阅源：每个 aCMS 站点一个 js + 一份配置 json + index.js
# 网络层做多后端兼容：$fetch / $http / req / request / http.get / okhttp / 全局 fetch
import json, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
os.makedirs(SRC, exist_ok=True)

HOST = "https://yueairhui.github.io"

sites = [
    ("juliang", "巨量4K", "https://api.juliang.live/api/provide/vod/"),
    ("iqiyi", "爱奇艺", "https://iqiyizyapi.com/api.php/provide/vod/"),
    ("maoyan", "猫眼", "https://api.maoyanapi.top/api.php/provide/vod/"),
    ("san360", "360", "https://360zy.com/api.php/provide/vod/"),
    ("zuid", "最大", "https://api.zuidapi.com/api/provide/vod/"),
    ("baidu", "百度", "https://api.apibdzy.com/api/provide/vod/"),
    ("hongniu", "红牛", "https://www.hongniuzy2.com/api.php/provide/vod/"),
]

TMPL = r"""// %(name)s — AppleCMS -> NowShowTime JS 源 (generated, multi-runtime)
const BASE = %(base)s;
const NAME = %(namejs)s;
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
"""

for old in glob.glob(os.path.join(SRC, "*.js")):
    os.remove(old)

cfg_sites = []
for key, name, base in sites:
    js_url = "%s/src/%s.js" % (HOST, key)
    with open(os.path.join(SRC, key + ".js"), "w", encoding="utf-8") as f:
        f.write(TMPL % {"name": name, "namejs": json.dumps(name, ensure_ascii=False), "base": json.dumps(base)})
    cfg_sites.append({
        "key": key, "name": name, "type": 3,
        "api": js_url, "js": js_url, "script": js_url, "url": js_url,
        "ext": "", "searchable": 1, "quickSearch": 1, "filterable": 1,
        "playerType": "", "icon": "",
    })

# yb.json —— TVBox/CatVod 配置：type=1 CMS 接口直连（映盒「添加猫源」用这个）
cms_sites = []
for key, name, base in sites:
    cms_sites.append({
        "key": key, "name": name, "type": 1, "api": base,
        "searchable": 1, "quickSearch": 1, "filterable": 1,
    })
cfg = {"name": "野人影视源", "sites": cms_sites, "parses": [], "lives": []}
with open(os.path.join(ROOT, "yb.json"), "w", encoding="utf-8") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=1)

# yb-script.json —— type=3 + JS 脚本地址（若 App 支持 js 源则用这份）
cfg_js = {"name": "野人影视源JS", "sites": cfg_sites, "parses": [], "lives": []}
with open(os.path.join(ROOT, "yb-script.json"), "w", encoding="utf-8") as f:
    json.dump(cfg_js, f, ensure_ascii=False, indent=1)

print("generated", len(cfg_sites), "js files")

# 映盒/猫影视 index.js（脚本源入口）
idx = []
idx.append("/* 野人影视源 index.js for 映盒/CatVod-style script source */")
idx.append("var sites = " + json.dumps(cfg_sites, ensure_ascii=False, indent=1) + ";")
idx.append("var parses = [];")
idx.append("var lives = [];")
idx.append("var config = { name: " + json.dumps(cfg["name"], ensure_ascii=False) + ", sites: sites, parses: parses, lives: lives };")
idx.append("if (typeof module !== 'undefined' && module.exports) { module.exports = config; }")
with open(os.path.join(ROOT, "index.js"), "w", encoding="utf-8") as f:
    f.write("\n".join(idx) + "\n")
print("wrote index.js")
