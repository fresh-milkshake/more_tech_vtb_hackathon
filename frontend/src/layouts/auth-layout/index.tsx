import { Outlet } from 'react-router-dom';
import styles from './auth-layout.module.scss';

export const AuthLayout = () => (
  <div className={styles.layout}>
    <Outlet />
  </div>
);
