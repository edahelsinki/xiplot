parcelRequire=function(e,r,t,n){var i,o="function"==typeof parcelRequire&&parcelRequire,u="function"==typeof require&&require;function f(t,n){if(!r[t]){if(!e[t]){var i="function"==typeof parcelRequire&&parcelRequire;if(!n&&i)return i(t,!0);if(o)return o(t,!0);if(u&&"string"==typeof t)return u(t);var c=new Error("Cannot find module '"+t+"'");throw c.code="MODULE_NOT_FOUND",c}p.resolve=function(r){return e[t][1][r]||r},p.cache={};var l=r[t]=new f.Module(t);e[t][0].call(l.exports,p,l,l.exports,this)}return r[t].exports;function p(e){return f(p.resolve(e))}}f.isParcelRequire=!0,f.Module=function(e){this.id=e,this.bundle=f,this.exports={}},f.modules=e,f.cache=r,f.parent=o,f.register=function(r,t){e[r]=[function(e,r){r.exports=t},{}]};for(var c=0;c<t.length;c++)try{f(t[c])}catch(e){i||(i=e)}if(t.length){var l=f(t[t.length-1]);"object"==typeof exports&&"undefined"!=typeof module?module.exports=l:"function"==typeof define&&define.amd?define(function(){return l}):n&&(this[n]=l)}if(parcelRequire=f,i)throw i;return f}({"ZXZ8":[function(require,module,exports) {
var e=this&&this.__awaiter||function(e,t,r,n){return new(r||(r=Promise))(function(s,o){function a(e){try{l(n.next(e))}catch(t){o(t)}}function u(e){try{l(n.throw(e))}catch(t){o(t)}}function l(e){var t;e.done?s(e.value):(t=e.value,t instanceof r?t:new r(function(e){e(t)})).then(a,u)}l((n=n.apply(e,t||[])).next())})},t=this&&this.__generator||function(e,t){var r,n,s,o,a={label:0,sent:function(){if(1&s[0])throw s[1];return s[1]},trys:[],ops:[]};return o={next:u(0),throw:u(1),return:u(2)},"function"==typeof Symbol&&(o[Symbol.iterator]=function(){return this}),o;function u(u){return function(l){return function(u){if(r)throw new TypeError("Generator is already executing.");for(;o&&(o=0,u[0]&&(a=0)),a;)try{if(r=1,n&&(s=2&u[0]?n.return:u[0]?n.throw||((s=n.return)&&s.call(n),0):n.next)&&!(s=s.call(n,u[1])).done)return s;switch(n=0,s&&(u=[2&u[0],s.value]),u[0]){case 0:case 1:s=u;break;case 4:return a.label++,{value:u[1],done:!1};case 5:a.label++,n=u[1],u=[0];continue;case 7:u=a.ops.pop(),a.trys.pop();continue;default:if(!(s=(s=a.trys).length>0&&s[s.length-1])&&(6===u[0]||2===u[0])){a=0;continue}if(3===u[0]&&(!s||u[1]>s[0]&&u[1]<s[3])){a.label=u[1];break}if(6===u[0]&&a.label<s[1]){a.label=s[1],s=u;break}if(s&&a.label<s[2]){a.label=s[2],a.ops.push(u);break}s[2]&&a.ops.pop(),a.trys.pop();continue}u=t.call(e,a)}catch(l){u=[6,l],n=0}finally{r=s=0}if(5&u[0])throw u[1];return{value:u[0]?u[1]:void 0,done:!0}}([u,l])}}},r=this&&this.__rest||function(e,t){var r={};for(var n in e)Object.prototype.hasOwnProperty.call(e,n)&&t.indexOf(n)<0&&(r[n]=e[n]);if(null!=e&&"function"==typeof Object.getOwnPropertySymbols){var s=0;for(n=Object.getOwnPropertySymbols(e);s<n.length;s++)t.indexOf(n[s])<0&&Object.prototype.propertyIsEnumerable.call(e,n[s])&&(r[n[s]]=e[n[s]])}return r};importScripts("https://cdn.jsdelivr.net/pyodide/v0.24.0/full/pyodide.js"),onmessage=function(c){return e(void 0,void 0,void 0,function(){var e,i,f,p,d,y,h,b,v,g,m,w,k;return t(this,function(t){switch(t.label){case 0:e=c.data,i=e.uuid,f=e.python,p=r(e,["uuid","python"]),t.label=1;case 1:return t.trys.push([1,12,,13]),[4,n];case 2:for(d=t.sent(),y=f,h=0,b=Object.keys(p);h<b.length;h++)v=b[h],self[v]=p[v];return[4,d.loadPackagesFromImports(y,{messageCallback:u,errorCallback:l})];case 3:t.sent(),g=void 0,t.label=4;case 4:0,t.label=5;case 5:return t.trys.push([5,7,,10]),[4,d.runPython(y)];case 6:return g=t.sent(),[3,11];case 7:return m=t.sent(),[4,d.runPython("import sys; None if not isinstance(sys.last_value, ImportError) else sys.last_value.name")];case 8:if(!(w=t.sent()))throw m;return[4,d.loadPackage(w,{messageCallback:u,errorCallback:l})];case 9:return t.sent(),[3,10];case 10:return[3,4];case 11:return g instanceof d.ffi.PyProxy&&(g=s(g)),o(i,g),[3,13];case 12:return k=t.sent(),a(i,k.message),[3,13];case 13:return[2]}})})};var n=loadPyodide({fullStdLib:!1,stdout:u,stderr:l});function s(e){var t=e.get_data(!1).toJs(),r=new TextDecoder("utf-8",{fatal:!0}),n=null;if(t)try{n=r.decode(t)}catch(u){n=t}n=n||null;var s=e.status_code,o=e.headers.keys(),a=Array.from(o).reduce(function(t,r){return t[r]=e.headers.get(r),t},{});return o.destroy(),e.destroy(),{response:n,status:s,headers:a}}function o(e,t){self.postMessage({uuid:e,results:t})}function a(e,t){self.postMessage({uuid:e,error:t})}function u(e){self.postMessage({consoleMessage:e})}function l(e){self.postMessage({consoleError:e})}
},{}]},{},["ZXZ8"], null)
//# sourceMappingURL=worker.660e5525.js.map