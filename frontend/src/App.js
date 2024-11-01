import './App.css';
import { ChatUI } from './components/Chat';
import { AuthForm } from './components/Login';
import { PrivateRoute } from './PrivateRoute/PrivateRoute';

function App() {
  return (
    <div className="App">
      
      <PrivateRoute Component={<ChatUI/>} FallbackComponent={<AuthForm/>}/>
    </div>
  );
}

export default App;
