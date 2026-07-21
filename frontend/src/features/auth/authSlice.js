import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { authApi } from '../../services/api/authApi'

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const response = await authApi.login(email, password)
      const { access, refresh } = response.data
      localStorage.setItem('accessToken', access)
      localStorage.setItem('refreshToken', refresh)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Login failed')
    }
  }
)

export const register = createAsyncThunk(
  'auth/register',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await authApi.register(userData)
      const { tokens } = response.data
      if (tokens) {
        localStorage.setItem('accessToken', tokens.access)
        localStorage.setItem('refreshToken', tokens.refresh)
      }
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Registration failed')
    }
  }
)

export const fetchCurrentUser = createAsyncThunk(
  'auth/fetchCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authApi.getCurrentUser()
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data)
    }
  }
)

/**
 * Enregistre les modifications du profil.
 *
 * Renvoie l'utilisateur complet tel que le serveur l'a écrit, jamais la
 * charge utile envoyée : c'est ce qui garantit que le solde de points affiché
 * reste celui du grand livre, même si le formulaire ne le connaissait pas.
 */
export const updateProfile = createAsyncThunk(
  'auth/updateProfile',
  async (payload, { rejectWithValue }) => {
    try {
      const response = await authApi.updateProfile(payload)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data)
    }
  }
)

export const changePassword = createAsyncThunk(
  'auth/changePassword',
  async ({ oldPassword, newPassword, newPasswordConfirm }, { rejectWithValue }) => {
    try {
      const response = await authApi.changePassword(
        oldPassword, newPassword, newPasswordConfirm
      )
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data)
    }
  }
)

export const logoutUser = createAsyncThunk(
  'auth/logout',
  // La déconnexion n'échoue jamais du point de vue de l'utilisateur : les
  // jetons sont purgés dans le `finally` quoi qu'il arrive, d'où l'absence de
  // `rejectWithValue`.
  async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken')
      if (refreshToken) {
        await authApi.logout(refreshToken)
      }
    } catch (error) {
      // Continue logout even if API call fails
      console.error('Logout API error:', error)
    } finally {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
    }
  }
)

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    isAuthenticated: false,
    // Passe à true dès que la question « qui est connecté ? » a reçu une
    // réponse, succès *ou* échec. Sans ce drapeau, une garde de rôle ne peut
    // pas distinguer « profil pas encore chargé » de « chargement échoué »,
    // et resterait bloquée sur un écran de chargement en cas de panne réseau.
    initialized: false,
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    setAuthenticated: (state, action) => {
      state.isAuthenticated = action.payload
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state) => {
        state.loading = false
        state.isAuthenticated = true
        state.error = null
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
        state.isAuthenticated = false
      })
      // Register
      .addCase(register.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false
        state.initialized = true
        state.user = action.payload.user
        state.isAuthenticated = true
        state.error = null
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      // Fetch Current User
      .addCase(fetchCurrentUser.pending, (state) => {
        state.loading = true
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.loading = false
        state.initialized = true
        state.user = action.payload
        state.isAuthenticated = true
      })
      .addCase(fetchCurrentUser.rejected, (state) => {
        state.loading = false
        state.initialized = true
        state.isAuthenticated = false
        state.user = null
      })
      // Mise à jour du profil : on remplace l'utilisateur par la version
      // renvoyée par le serveur, pas par ce qu'on lui a envoyé.
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.user = action.payload
        state.error = null
      })
      // Logout
      .addCase(logoutUser.fulfilled, (state) => {
        state.user = null
        state.isAuthenticated = false
        state.initialized = true
        state.error = null
      })
  },
})

export const { clearError, setAuthenticated } = authSlice.actions
export default authSlice.reducer
