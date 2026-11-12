import {reactive} from 'vue';import {request} from '../api/client';import type {User} from '../types/domain';
export const auth=reactive({user:JSON.parse(localStorage.getItem('settlement-user')||'null') as User|null,error:''});
export async function login(email:string,password:string){const r=await request('/auth/login','POST',{email,password});localStorage.setItem('settlement-token',r.token);localStorage.setItem('settlement-user',JSON.stringify(r.user));auth.user=r.user}
export function logout(){localStorage.removeItem('settlement-token');localStorage.removeItem('settlement-user');auth.user=null;location.hash='#/login'}
export const canWrite=()=>auth.user?.role!=='viewer';export const isAdmin=()=>auth.user?.role==='admin';
