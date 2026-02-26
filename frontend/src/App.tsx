import { Outlet } from 'react-router-dom';
import './App.css';
import Header from './components/header';
// import Logout from './features/auth/components/logout';

function App() {
  return (
    <>
      <Outlet />
      
    </>
  );
}

export default App;