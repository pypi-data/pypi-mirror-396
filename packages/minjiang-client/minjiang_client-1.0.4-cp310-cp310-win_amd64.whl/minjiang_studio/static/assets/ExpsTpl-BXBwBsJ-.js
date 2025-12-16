import{bd as B,bb as C,bg as I,bf as le,bw as ce,d as E,I as O,bo as ue,bp as te,bx as de,by as pe,ad as me,L as N,bu as _e,r as b,o as ve,b9 as fe,bz as he,bA as be,b0 as ge,e as R,f as y,h as d,aM as xe,b as we,C as ye,a3 as ke,i as h,W as Ce,l as s,V as U,w as m,v as Se,B as Te,aq as ze,a9 as X,af as Y,a7 as D,ap as Be,aQ as Re,t as F,ak as Ee,aj as Le,a8 as $e,s as Z,b1 as W,F as ee,E as qe,a2 as Ve}from"./index-BHd9xypC.js";import{j as je,k as Ie,l as Oe,n as Pe}from"./RecordStop24Regular-Qo7SzBWJ.js";import{l as Ae}from"./exp-VCEEBlLK.js";import{_ as Fe}from"./DynamicForm.vue_vue_type_script_setup_true_lang-jtwxeB2H.js";const He=B("breadcrumb",`
 white-space: nowrap;
 cursor: default;
 line-height: var(--n-item-line-height);
`,[C("ul",`
 list-style: none;
 padding: 0;
 margin: 0;
 `),C("a",`
 color: inherit;
 text-decoration: inherit;
 `),B("breadcrumb-item",`
 font-size: var(--n-font-size);
 transition: color .3s var(--n-bezier);
 display: inline-flex;
 align-items: center;
 `,[B("icon",`
 font-size: 18px;
 vertical-align: -.2em;
 transition: color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 `),C("&:not(:last-child)",[le("clickable",[I("link",`
 cursor: pointer;
 `,[C("&:hover",`
 background-color: var(--n-item-color-hover);
 `),C("&:active",`
 background-color: var(--n-item-color-pressed); 
 `)])])]),I("link",`
 padding: 4px;
 border-radius: var(--n-item-border-radius);
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 position: relative;
 `,[C("&:hover",`
 color: var(--n-item-text-color-hover);
 `,[B("icon",`
 color: var(--n-item-text-color-hover);
 `)]),C("&:active",`
 color: var(--n-item-text-color-pressed);
 `,[B("icon",`
 color: var(--n-item-text-color-pressed);
 `)])]),I("separator",`
 margin: 0 8px;
 color: var(--n-separator-color);
 transition: color .3s var(--n-bezier);
 user-select: none;
 -webkit-user-select: none;
 `),C("&:last-child",[I("link",`
 font-weight: var(--n-font-weight-active);
 cursor: unset;
 color: var(--n-item-text-color-active);
 `,[B("icon",`
 color: var(--n-item-text-color-active);
 `)]),I("separator",`
 display: none;
 `)])])]),ae=ce("n-breadcrumb"),Me=Object.assign(Object.assign({},te.props),{separator:{type:String,default:"/"}}),st=E({name:"Breadcrumb",props:Me,setup(e){const{mergedClsPrefixRef:c,inlineThemeDisabled:n}=ue(e),_=te("Breadcrumb","-breadcrumb",He,de,e,c);pe(ae,{separatorRef:me(e,"separator"),mergedClsPrefixRef:c});const x=N(()=>{const{common:{cubicBezierEaseInOut:v},self:{separatorColor:p,itemTextColor:i,itemTextColorHover:l,itemTextColorPressed:g,itemTextColorActive:L,fontSize:k,fontWeightActive:f,itemBorderRadius:P,itemColorHover:A,itemColorPressed:H,itemLineHeight:w}}=_.value;return{"--n-font-size":k,"--n-bezier":v,"--n-item-text-color":i,"--n-item-text-color-hover":l,"--n-item-text-color-pressed":g,"--n-item-text-color-active":L,"--n-separator-color":p,"--n-item-color-hover":A,"--n-item-color-pressed":H,"--n-item-border-radius":P,"--n-font-weight-active":f,"--n-item-line-height":w}}),t=n?_e("breadcrumb",void 0,x,e):void 0;return{mergedClsPrefix:c,cssVars:n?void 0:x,themeClass:t==null?void 0:t.themeClass,onRender:t==null?void 0:t.onRender}},render(){var e;return(e=this.onRender)===null||e===void 0||e.call(this),O("nav",{class:[`${this.mergedClsPrefix}-breadcrumb`,this.themeClass],style:this.cssVars,"aria-label":"Breadcrumb"},O("ul",null,this.$slots))}});function Ue(e=he?window:null){const c=()=>{const{hash:x,host:t,hostname:v,href:p,origin:i,pathname:l,port:g,protocol:L,search:k}=(e==null?void 0:e.location)||{};return{hash:x,host:t,hostname:v,href:p,origin:i,pathname:l,port:g,protocol:L,search:k}},n=b(c()),_=()=>{n.value=c()};return ve(()=>{e&&(e.addEventListener("popstate",_),e.addEventListener("hashchange",_))}),fe(()=>{e&&(e.removeEventListener("popstate",_),e.removeEventListener("hashchange",_))}),n}const De={separator:String,href:String,clickable:{type:Boolean,default:!0},onClick:Function},it=E({name:"BreadcrumbItem",props:De,slots:Object,setup(e,{slots:c}){const n=be(ae,null);if(!n)return()=>null;const{separatorRef:_,mergedClsPrefixRef:x}=n,t=Ue(),v=N(()=>e.href?"a":"span"),p=N(()=>t.value.href===e.href?"location":null);return()=>{const{value:i}=x;return O("li",{class:[`${i}-breadcrumb-item`,e.clickable&&`${i}-breadcrumb-item--clickable`]},O(v.value,{class:`${i}-breadcrumb-item__link`,"aria-current":p.value,href:e.href,onClick:e.onClick},c),O("span",{class:`${i}-breadcrumb-item__separator`,"aria-hidden":"true"},ge(c.separator,()=>{var l;return[(l=e.separator)!==null&&l!==void 0?l:_.value]})))}}}),Ne={xmlns:"http://www.w3.org/2000/svg","xmlns:xlink":"http://www.w3.org/1999/xlink",viewBox:"0 0 512 512"},Ke=E({name:"CloseCircleOutline",render:function(c,n){return y(),R("svg",Ne,n[0]||(n[0]=[d("path",{d:"M448 256c0-106-86-192-192-192S64 150 64 256s86 192 192 192s192-86 192-192z",fill:"none",stroke:"currentColor","stroke-miterlimit":"10","stroke-width":"32"},null,-1),d("path",{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"32",d:"M320 320L192 192"},null,-1),d("path",{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"32",d:"M192 320l128-128"},null,-1)]))}}),Ge={xmlns:"http://www.w3.org/2000/svg","xmlns:xlink":"http://www.w3.org/1999/xlink",viewBox:"0 0 512 512"},lt=E({name:"Duplicate",render:function(c,n){return y(),R("svg",Ge,n[0]||(n[0]=[d("path",{d:"M408 112H184a72 72 0 0 0-72 72v224a72 72 0 0 0 72 72h224a72 72 0 0 0 72-72V184a72 72 0 0 0-72-72zm-32.45 200H312v63.55c0 8.61-6.62 16-15.23 16.43A16 16 0 0 1 280 376v-64h-63.55c-8.61 0-16-6.62-16.43-15.23A16 16 0 0 1 216 280h64v-63.55c0-8.61 6.62-16 15.23-16.43A16 16 0 0 1 312 216v64h64a16 16 0 0 1 16 16.77c-.42 8.61-7.84 15.23-16.45 15.23z",fill:"currentColor"},null,-1),d("path",{d:"M395.88 80A72.12 72.12 0 0 0 328 32H104a72 72 0 0 0-72 72v224a72.12 72.12 0 0 0 48 67.88V160a80 80 0 0 1 80-80z",fill:"currentColor"},null,-1)]))}}),Je={xmlns:"http://www.w3.org/2000/svg","xmlns:xlink":"http://www.w3.org/1999/xlink",viewBox:"0 0 24 24"},ct=E({name:"Home24Filled",render:function(c,n){return y(),R("svg",Je,n[0]||(n[0]=[d("g",{fill:"none"},[d("path",{d:"M10.55 2.533a2.25 2.25 0 0 1 2.9 0l6.75 5.695c.508.427.8 1.056.8 1.72v9.802a1.75 1.75 0 0 1-1.75 1.75h-3a1.75 1.75 0 0 1-1.75-1.75v-5a.75.75 0 0 0-.75-.75h-3.5a.75.75 0 0 0-.75.75v5a1.75 1.75 0 0 1-1.75 1.75h-3A1.75 1.75 0 0 1 3 19.75V9.947c0-.663.292-1.292.8-1.72l6.75-5.694z",fill:"currentColor"})],-1)]))}}),Qe={class:"absolute top-1 right-1"},Xe={class:"pl-5 h-full tpl-s-g"},Ye={class:"mb-5"},Ze={class:"text-xl"},We={class:"text-sm opacity-80"},et={class:"flex justify-end items-center gap-2 mt-2 mr-[20px]"},tt=E({__name:"ExpsTpl",props:{fid:{}},setup(e,{expose:c}){const n=e,_=xe(),{t:x}=we(),t=ye(),v=b(),p=b(!1),i=b(!1),l=b(!1),g=b(!1),L=()=>{g.value=!0},k=()=>{g.value=!1},f=b(),P=b(),A=b(),H=async()=>{const[r,a]=await je();!r&&(a==null?void 0:a.status)===0&&(A.value=a.data,f.value=Object.keys(a.data)[0],K(f.value))},w=b(),M=b(),K=async r=>{const[a,o]=await Ie({template_group_name:r});!a&&(o==null?void 0:o.status)===0&&(P.value=o.data,w.value=Object.keys(o.data)[0],G(Object.keys(o.data)[0]))},G=async r=>{if(l.value)return;l.value=!0;const[a,o]=await Oe({template_group_name:f.value,template_name:r,group_name:t.query.device_group_name,space_id:t.query.space_id});l.value=!1,!a&&(o==null?void 0:o.status)===0&&(M.value=o.data)},ne=r=>{K(r)},oe=r=>{G(r)},re=async()=>{var S;if(p.value||!v.value)return;p.value=!0;let r={};try{r=await((S=v.value[0])==null?void 0:S.submit())}catch{p.value=!1;return}const a=W(r);if(ee(a))return;const{device_group_name:o,space_id:$,task_id:q}=t.query,[z,u]=await Pe({setting:a,task_id:q,group_name:o,space_id:$,template_group:f.value,template_name:w.value,exp_folder_id:+String(n.fid)});p.value=!1,!z&&(u==null?void 0:u.status)===0&&(u.data.exp.template=u.data.exp.template||`${f.value}/${w.value}`,qe(()=>{setTimeout(()=>{localStorage.setItem("t",JSON.stringify(u));const T=new URLSearchParams({device_group_name:t.query.device_group_name,task_id:t.query.task_id,task_title:t.query.task_title,space_id:t.query.space_id,create:"1",fid:String(n.fid)});window.open(`/experiment/expSettings?${T.toString()}`,_.expOpenForm)},100),k()}))},se=async()=>{var S;if(i.value||!v.value)return;i.value=!0;let r={};try{r=await((S=v.value[0])==null?void 0:S.submit())}catch{i.value=!1;return}const a=W(r);if(ee(a))return;const{device_group_name:o,space_id:$,task_id:q}=t.query,[z,u]=await Ae({setting:a,task_id:q,group_name:o,space_id:$,template_group:f.value,template_name:w.value,exp_folder_id:+String(n.fid)});i.value=!1,!z&&(u==null?void 0:u.status)===0&&(setTimeout(()=>{const T=new URLSearchParams({device_group_name:t.query.device_group_name,task_id:t.query.task_id,task_title:t.query.task_title,space_id:t.query.space_id,exp_id:String(u.data.exp_id)});window.open(`/experiment/plotter?${T.toString()}`,_.expOpenForm)},100),k())};return ke(g,r=>{r&&H()},{immediate:!0}),c({open:L,close:k}),(r,a)=>{const o=Te,$=Le,q=Ee,z=Be,u=ze,S=Re,T=Se,ie=Ce;return y(),R("div",null,[h(ie,{show:s(g),"onUpdate:show":a[2]||(a[2]=V=>U(g)?g.value=V:null),size:"huge"},{default:m(()=>[h(T,{style:{"min-height":"700px",height:"calc(100vh - 100px)","box-sizing":"border-box",overflow:"hidden",width:"80vw","min-width":"600px",padding:"12px",position:"relative"},"content-class":"!pb-0"},{default:m(()=>[d("div",Qe,[h(o,{type:"primary",onClick:k,size:"small",circle:""},{icon:m(()=>[h(s(Ke))]),_:1})]),h(u,{type:"card",placement:"left",animated:"",onUpdateValue:ne,value:s(f),"onUpdate:value":a[1]||(a[1]=V=>U(f)?f.value=V:null),style:{height:"calc(100vh - 160px)"}},{default:m(()=>[(y(!0),R(X,null,Y(s(A),(V,J)=>(y(),D(z,{key:J,name:J,tab:V.title,disabled:s(l)},{default:m(()=>[h(S,{style:{height:"100%","padding-top":"10px","box-sizing":"border-box"}},{default:m(()=>[h(u,{type:"line",placement:"left",value:s(w),"onUpdate:value":a[0]||(a[0]=j=>U(w)?w.value=j:null),onUpdateValue:oe,style:{height:"100%"}},{default:m(()=>[(y(!0),R(X,null,Y(s(P),(j,Q)=>(y(),D(z,{key:Q,name:Q,tab:j.title,disabled:s(l)},{default:m(()=>[d("div",Xe,[d("div",Ye,[d("div",Ze,F(j.title),1),d("div",We,F(j.desc),1)]),h(q,{show:s(l)},{default:m(()=>[h($,{style:{"padding-right":"20px"}},{default:m(()=>[s(M)&&!s(l)?(y(),D(Fe,{key:0,cfgs:s(M),ref_for:!0,ref_key:"dynamicFormRef",ref:v},null,8,["cfgs"])):$e("",!0)]),_:1}),d("div",et,[h(o,{loading:s(i),disabled:s(p),type:"primary",onClick:se},{default:m(()=>[Z(F(s(x)("groupDetail.exps.createsubmit")),1)]),_:1},8,["loading","disabled"]),h(o,{loading:s(p),disabled:s(i),type:"primary",onClick:re},{default:m(()=>[Z(F(s(x)("groupDetail.exps.createExpBtn")),1)]),_:1},8,["loading","disabled"])])]),_:1},8,["show"])])]),_:2},1032,["name","tab","disabled"]))),128))]),_:1},8,["value"])]),_:1})]),_:2},1032,["name","tab","disabled"]))),128))]),_:1},8,["value"])]),_:1})]),_:1},8,["show"])])}}}),ut=Ve(tt,[["__scopeId","data-v-5be5eb4a"]]);export{lt as D,ut as E,ct as H,st as _,it as a};
