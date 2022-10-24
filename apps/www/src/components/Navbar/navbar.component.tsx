import { Button } from '../Button';
import { Link } from './link';

export function Navbar() {
  return (
    <nav className="flex items-center py-10">
      <h2 className="text-orange-100">NOCELLOS</h2>
      <ul className="flex items-center gap-10 mx-12 ml-auto">
        <li>
          <Link href="/" text="Tasks" />
        </li>
        <li>
          <Link href="/my-cards" text="My cards" />
        </li>
        <li>
          <Link href="/stats" text="Stats" />
        </li>
      </ul>
      <Button text="Sign in" />
    </nav>
  );
}
