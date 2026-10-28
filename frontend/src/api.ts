import type { InvestigationResult } from "./types";
const API_BASE=(import.meta.env.VITE_API_BASE_URL as string|undefined)??"http://127.0.0.1:8000";
export async function investigateProject(file:File):Promise<InvestigationResult>{
 const form=new FormData();form.append("file",file);
 const response=await fetch(`${API_BASE}/api/investigations`,{method:"POST",body:form});
 if(!response.ok){const body=await response.json().catch(()=>({}));throw new Error(body.detail??`Request failed (${response.status})`);}
 return response.json() as Promise<InvestigationResult>;
}
