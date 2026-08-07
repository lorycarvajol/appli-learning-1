import Header from './Header';
import Footer from './Footer';
import ScrollToTopButton from '../ui/ScrollToTopButton';
import ErrorBoundary from '../ui/ErrorBoundary';
import BadgeRevealModal from '@/features/gamification/BadgeRevealModal';
import './Layout.css';

export default function Layout({ children }) {
  return (
    <div className="layout">
      <a href="#main-content" className="skip-link">
        Aller au contenu principal
      </a>
      <Header />
      <main className="layout__main" id="main-content" tabIndex={-1}>
        {/*
          La frontière est **à l'intérieur** du `main`, pas autour du `Layout` :
          une page qui casse laisse ainsi l'en-tête et le pied en place, donc
          la navigation. Placée plus haut, elle emporterait tout et ne
          laisserait qu'un message isolé.
          Une seconde frontière enveloppe `<Routes>` dans `App.jsx` — elle
          couvre les pages publiques, qui ne passent pas par `Layout`, et
          rattrape le cas où l'en-tête lui-même casserait.
        */}
        <ErrorBoundary>{children}</ErrorBoundary>
      </main>
      <Footer />
      <ScrollToTopButton />
      {/* Monté une seule fois : consomme la file de révélation où qu'on soit */}
      <BadgeRevealModal />
    </div>
  );
}
