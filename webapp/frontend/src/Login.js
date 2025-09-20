import React, { useState } from 'react';
import { Link } from "react-router-dom";
import './Login.css';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

    const handleSubmit = async (event) => {
        event.preventDefault(); // Prevent default form submission behavior
    
        try {
            const response = await fetch(`/api/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });
    
            if (response.ok) {
                // Login successful
                const responseData = await response.json();
                console.log('Login successful:', responseData);
    
                // Store the token in localStorage
                localStorage.setItem('token', responseData.token);
                localStorage.setItem('user', JSON.stringify(responseData.user));
    
                window.location.href = '/profile';
            } else {
                // Login failed
                const errorData = await response.json();
                console.error('Login failed:', errorData);
                setError('Invalid username or password');
            }
        } catch (error) {
            console.error('Error during login:', error);
            setError('Something went wrong. Please try again later.');
        }
    };
    

    return (
        <div className="box">
            <h1>Login</h1>
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="username">Username:</label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Login</button>
                <div className="create-account-link">
                    <Link to="/signup">Or create an account if you aren't registered</Link>
                </div>
            </form>
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    );
};

export default Login;
