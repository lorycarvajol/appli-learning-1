import Header from './Header';
import Footer from './Footer';
import ScrollToTopButton from '../ui/ScrollToTopButton';
import './Layout.css';

export default function Layout({ children }) {
  return (
    <div className="layout">
      <a href="#main-content" className="skip-link">
        Aller au contenu principal
      </a>
      <Header />
      <main className="layout__main" id="main-content" tabIndex={-1}>
        {children}
      </main>
      <Footer />
      <ScrollToTopButton />
    </div>
  );
}
