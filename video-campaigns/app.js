const list=document.querySelector('#video-list');
const searchInput=document.querySelector('#search');
const categorySelect=document.querySelector('#category');
const categoryIndex=document.querySelector('#category-index');
const summary=document.querySelector('#inventory-summary');
const empty=document.querySelector('#empty');
let catalog;
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const sortedVideos=()=>catalog.videos.filter(v=>!v.excludeFromCampaignViewer).sort((a,b)=>(a.editorialOrder??a._sourceOrder)-(b.editorialOrder??b._sourceOrder));
function draw(){
 const category=categorySelect.value;
 const query=searchInput.value.trim().toLocaleLowerCase();
 const items=sortedVideos().filter(v=>(!category||v.categories.includes(category))&&(!query||[v.title,v.displayTitle,v.publicDescription??v.description,v.videoId,...v.categories].join(' ').toLocaleLowerCase().includes(query)));
 list.innerHTML=items.map((v,i)=>`<article class="video-card">
   <div class="number">${String(i+1).padStart(3,'0')}</div>
   <div><h3 class="video-title">${esc(v.displayTitle||v.title)}</h3>
     <div class="tags">${v.categories.map(c=>`<span class="tag">${esc(c)}</span>`).join('')}</div>
     ${(v.publicDescription??v.description)?`<p class="video-description">${esc(v.publicDescription??v.description)}</p>`:''}
     <div class="video-meta"><span>YouTube ID: ${esc(v.videoId)}</span></div>
     
     ${v.additionalSources.map(s=>`<div class="project-reference"><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.label)}</a></div>`).join('')}
   </div>
   <div class="video-links"><a href="${esc(v.url)}" target="_blank" rel="noopener noreferrer">Open on YouTube <span class="link-arrow" aria-hidden="true">↗</span></a></div>
 </article>`).join('');
 summary.textContent=`${items.length} of ${catalog.videos.filter(v=>!v.excludeFromCampaignViewer).length} videos`;
 empty.hidden=items.length!==0;
}
async function init(){
 try{
  const response=await fetch('/video-campaigns/videos.json',{cache:'no-store'});
  if(!response.ok)throw new Error('Inventory could not be loaded.');
  catalog=await response.json();
  catalog.videos.forEach((v,i)=>v._sourceOrder=i);
  for(const c of catalog.categories){const option=document.createElement('option');option.value=c;option.textContent=c;categorySelect.append(option);const button=document.createElement('button');button.type='button';button.className='category-chip';button.textContent=`${c} · ${catalog.videos.filter(v=>!v.excludeFromCampaignViewer&&v.categories.includes(c)).length}`;button.setAttribute('aria-pressed','false');button.addEventListener('click',()=>{categorySelect.value=categorySelect.value===c?'':c;syncChips();draw()});categoryIndex.append(button)}
  draw();
 }catch(e){summary.textContent=e.message;list.innerHTML='';}
}
function syncChips(){for(const b of categoryIndex.children)b.setAttribute('aria-pressed',String(categorySelect.value&&b.textContent.startsWith(categorySelect.value+' ·')))}
searchInput.addEventListener('input',draw);
categorySelect.addEventListener('change',()=>{syncChips();draw()});
document.querySelector('#clear').addEventListener('click',()=>{searchInput.value='';categorySelect.value='';syncChips();draw();searchInput.focus()});
init();
