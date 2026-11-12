import {request} from "./client";export const fetchItems=()=>request("/items");export const createItems=(body:unknown)=>request("/items","POST",body);
