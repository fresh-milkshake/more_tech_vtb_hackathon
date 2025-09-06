export interface IAuthorizationRequestData {
  grant_type: 'password';
  username: string;
  password: string;
  scope?: string;
  client_id: string;
  client_secret: string;
}

export interface IAuthorizationCredentials {
  access_token: string;
  expires_in: number;
  token_type: string;
}

export interface IRegistrationRequestData {
  email: string;
  full_name: string;
  password: string;
}

export interface IRegistrationCredentials {
  email: string;
  full_name: string;
  id: number;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}
