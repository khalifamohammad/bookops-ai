import { Clock3, Mail, MapPin, Phone } from 'lucide-react';

export default function ContactPage() {
  return <section className="section page-section"><div className="section-heading centered"><span>Contact</span><h1>We are here to help</h1><p>Contact the business directly or use the booking page to reserve a time.</p></div><div className="contact-grid"><article><Phone/><h3>Phone</h3><p>+972 50 000 0000</p></article><article><Mail/><h3>Email</h3><p>hello@bookops.example</p></article><article><MapPin/><h3>Location</h3><p>Business address goes here</p></article><article><Clock3/><h3>Opening hours</h3><p>Sunday–Thursday, 09:00–18:00</p></article></div></section>;
}
