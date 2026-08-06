import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import { store } from './app/store.js'
import { ThemeProvider } from './contexts/ThemeProvider.jsx'
import './styles/main.scss'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider>
      <Provider store={store}>
        {/*
          Opt-in explicite au comportement React Router v7 : tait les
          avertissements de migration et aligne dès maintenant le routeur sur
          la prochaine majeure. `v7_startTransition` s'accorde bien avec le
          `Suspense` des routes chargées à la demande (transitions non
          bloquantes) ; `v7_relativeSplatPath` fige la résolution des routes
          relatives sous un splat.
        */}
        <BrowserRouter
          future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
        >
          <App />
        </BrowserRouter>
      </Provider>
    </ThemeProvider>
  </React.StrictMode>,
)
