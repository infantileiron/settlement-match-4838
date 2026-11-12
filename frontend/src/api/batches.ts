import {request} from "./client";export const fetchBatches=()=>request("/batches");export const createBatches=(body:unknown)=>request("/batches","POST",body);
