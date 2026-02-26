import type { LoginRequest, RegisterRequest, AuthResponse } from '../../../common/DataModels/User'
import api from '../../../lib/axios'
import type { Role } from '../../../common/DataModels/User'

export const loginUser = (data:LoginRequest) : Promise<AuthResponse> =>
    api.post<AuthResponse>('/auth/login', data).then((res) => {
        return res.data
    });

export const registerUser = (data:RegisterRequest) : Promise<{ message : string }> =>
    api.post<{ message : string}>('/auth/register',data).then((res) => res.data);

export const logoutUser = () : Promise<{ message : string }> =>
    api.get<{ message : string }>('/auth/logout').then((res) => res.data);

export const refreshToken = () : Promise<{access_token : string, token_type: string}> => 
    api.post<{access_token : string, token_type: string}>('/auth/refresh').then(res => res.data)

export const getRoles = (): Promise<Role[]> =>
    api.get<Role[]>('/users/get_roles').then((res) => res.data);

export default api;



