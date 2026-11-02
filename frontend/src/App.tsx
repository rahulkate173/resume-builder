import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from '@/store/useAuthStore'
import Landing from '@/pages/Landing'
import Login from '@/pages/Login'
import Register from '@/pages/Register'
import Dashboard from '@/pages/Dashboard'
import Editor from '@/pages/Editor'
import JDResumePage from '@/pages/JDResumePage'
import UploadResumePage from '@/pages/UploadResumePage'
import Navbar from '@/components/Navbar'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token)
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token)
  return token ? <Navigate to="/dashboard" replace /> : <>{children}</>
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#121215',
            color: '#fff',
            border: '1px solid #27272A',
            fontFamily: 'Inter, sans-serif',
            fontSize: '0.875rem',
          },
        }}
      />
      <Routes>
        {/* Public */}
        <Route path="/" element={<Landing />} />
        <Route path="/login"    element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

        {/* Protected */}
        <Route path="/dashboard"       element={<PrivateRoute><><Navbar /><Dashboard /></></PrivateRoute>} />
        <Route path="/editor/:id"      element={<PrivateRoute><><Navbar /><Editor /></></PrivateRoute>} />
        <Route path="/editor/new"      element={<PrivateRoute><><Navbar /><Editor /></></PrivateRoute>} />
        <Route path="/jd-resume"       element={<PrivateRoute><><Navbar /><JDResumePage /></></PrivateRoute>} />
        <Route path="/upload-resume"   element={<PrivateRoute><><Navbar /><UploadResumePage /></></PrivateRoute>} />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
