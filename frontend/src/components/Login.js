import { useState } from 'react'
import { Mail, Lock, Eye, EyeOff, LogIn, UserPlus } from 'lucide-react'
import {  toast } from 'react-toastify';
import { useAuth } from "../context/AuthContext";
import {usePostReq} from "../hooks/usePostReq";
import axios from "axios";


export const AuthForm = () => {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const { authStateChange } = useAuth();
  const {loading,execute} = usePostReq("auth/login");
  const {_loading,execute:_execute} = usePostReq("auth/signup");

  const handleSubmit = async(e) => {
    e.preventDefault();
    setError('');

    if (isLogin) {
      const response = await execute({email,password});
      if (response.access_token){
        await authStateChange();
        toast.success("Loggedin Sucessfully!");
      }
      else{
        toast.error("Credential Error!");
      }
    } else {
        const response = await _execute({ email, password });
        if (response.access_token) {
          await authStateChange();
          toast.success("Registered Sucessfully!");
        } else {
          toast.error("User already registered!");
        }
    }
  };


  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md">
        <form onSubmit={handleSubmit} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
          <h2 className="text-2xl font-bold mb-6 text-center">
            {isLogin ? 'Login' : 'Sign Up'}
          </h2>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
              <Mail className="inline mr-2" size={18} />
              Email
            </label>
            <div className="relative">
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline pl-10"
                id="email"
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
              <Lock className="inline mr-2" size={18} />
              Password
            </label>
            <div className="relative">
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline pl-10 pr-10"
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="******************"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <button
                type="button"
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>
          {!isLogin && (
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="confirmPassword">
                <Lock className="inline mr-2" size={18} />
                Confirm Password
              </label>
              <div className="relative">
                <input
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline pl-10"
                  id="confirmPassword"
                  type="password"
                  placeholder="******************"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              </div>
            </div>
          )}
          {error && <p className="text-red-500 text-xs italic mb-4">{error}</p>}
          <div className="flex items-center justify-between">
            <button
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline flex items-center"
              type="submit"
            >
              {isLogin ? <LogIn className="mr-2" size={18} /> : <UserPlus className="mr-2" size={18} />}
              {isLogin ? 'Sign In' : 'Sign Up'}
            </button>
            <button
              className="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800"
              type="button"
              onClick={() => {
                setIsLogin(!isLogin)
                setError('')
                setPassword('')
                setConfirmPassword('')
              }}
            >
              {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Login"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}