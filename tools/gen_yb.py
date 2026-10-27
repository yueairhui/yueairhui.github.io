#!/usr/bin/env python3
# 生成 映盒(NowShowTime) JS 订阅源：每个 aCMS 站点一个 js + 一份配置 json
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
os.makedirs(SRC, exist_ok=True)

HOST = "https://cdn.jsdelivr.net/gh/yueairhui/yueairhui.github.io@main"

sites = [
    ("juliang", "巨量4K", "https://api.juliang.live/api/provide/vod/"),
    ("iqiyi", "爱奇艺", "https://iqiyizyapi.com/api.php/provide/vod/"),
    ("maoyan", "猫眼", "https://api.maoyanapi.top/api.php/provide/vod/"),
    ("san360", "360", "https://360zy.com/api.php/provide/vod/"),
    ("zuid", "最大", "https://api.zuidapi.com/api.php/provide/vod/"),
    ("baidu", "百度", "https://api.apibdzy.com/api.php/provide/vod/"),
    ("hongniu", "红牛", "https://www.hongniuzy2.com/api.php/provide/vod/"),
]

TMPL = r"""// %(name)s — AppleCMS -> NowShowTime JS 源 (generated)
const BASE = %(base)s;
const NAME = %(namejs)s;
const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';

function _h() { return { 'User-Agent': UA, 'Accept': 'application/json,text/plain,*/*' }; }
function _q(s) { return BASE + (BASE.indexOf('?') > -1 ? '&' : '?') + s; }
function _j(r) {
  var d = (r && r.data !== undefined) ? r.data : r;
  if (!d) return {};
  if (typeof d === 'string') { try { return JSON.parse(d); } catch (e) { return {}; } }
  return d;
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
  var j = _j(await $fetch.get(_q('ac=list'), { headers: _h(), userAgent: UA }));
  var cls = (j.class || []).slice(0, 60).map(function (c) {
    return { id: String(c.type_id), name: c.type_name, ext: { url: _q('ac=detail&t=' + c.type_id + '&pg=1') } };
  });
  if (!cls.length) cls = [{ id: '1', name: '电影', ext: { url: _q('ac=detail&t=1&pg=1') } }];
  _cats = cls;
  return _cats;
}

function _ok(j) { return j && j.list && j.list.length; }

function _list(q, fallback) {
  return (async function () {
    var j = _j(await $fetch.get(_q('ac=detail&' + q), { headers: _h(), userAgent: UA }));
    if (!_ok(j)) j = _j(await $fetch.get(_q('ac=list&' + q), { headers: _h(), userAgent: UA }));
    if (!_ok(j)) j = _j(await $fetch.get(_q('ac=videolist&' + q), { headers: _h(), userAgent: UA }));
    if (!_ok(j) && fallback) {
      j = _j(await $fetch.get(_q('ac=detail&' + fallback), { headers: _h(), userAgent: UA }));
      if (!_ok(j)) j = _j(await $fetch.get(_q('ac=list&' + fallback), { headers: _h(), userAgent: UA }));
    }
    return j;
  })();
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
  if (/\.(m3u8|mp4)(\?|$)/i.test(episodeUrl)) return episodeUrl;
  try {
    var r = await $fetch.get(episodeUrl, { headers: { 'User-Agent': UA, 'Referer': episodeUrl }, userAgent: UA });
    var h = (r && r.data) || '';
    if (typeof h !== 'string') return episodeUrl;
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
    var j = _j(await $fetch.get(_q('ac=detail&ids=' + videoId), { headers: _h(), userAgent: UA }));
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
  var j = _j(await $fetch.get(_q('ac=detail&wd=' + encodeURIComponent(keyword) + '&pg=' + (page || 1)), { headers: _h(), userAgent: UA }));
  return _map(j.list);
}
"""

import glob
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

cfg = {"name": "野人影视源", "sites": cfg_sites, "parses": [], "lives": []}
with open(os.path.join(ROOT, "yb.json"), "w", encoding="utf-8") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=1)

print("generated", len(cfg_sites), "js files;", os.path.join(ROOT, "yb.json"))
