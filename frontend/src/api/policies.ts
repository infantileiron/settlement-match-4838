import {request} from "./client";export const fetchPolicies=()=>request("/policies");export const createPolicies=(body:unknown)=>request("/policies","POST",body);
