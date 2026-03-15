import { Link, Outlet, useLocation } from 'react-router-dom';

export default function Layout() {
  const location = useLocation();

  const isActive = (path: string) =>
    location.pathname === path ||
    (path !== '/' && location.pathname.startsWith(path))
      ? 'active'
      : '';

  return (
    <>
      <header className="app-header">
        <div className="header-inner">
          <div className="header-title">
            <Link to="/">PKD Scholar</Link>
          </div>
          <nav className="header-nav">
            <Link to="/studies" className={isActive('/studies')}>
              Studies
            </Link>
            <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
              Corpus
            </Link>
            <Link to="/topics" className={isActive('/topics')}>
              Topics
            </Link>
            <Link
              to="/search"
              className={location.pathname === '/search' ? 'active' : ''}
            >
              Search
            </Link>
          </nav>
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </>
  );
}
