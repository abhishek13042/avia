import type { Metadata } from "next";
import { Libre_Franklin, Stardos_Stencil } from "next/font/google";
import { SiteNav } from "@/components/SiteNav";
import "./globals.css";

const franklin = Libre_Franklin({ subsets: ["latin"], variable: "--font-franklin", display: "swap" });
const stencil = Stardos_Stencil({
  weight: "700",
  subsets: ["latin"],
  variable: "--font-stencil",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AVIA",
  description: "Segment, track and count apples in orchard video.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${franklin.variable} ${stencil.variable}`}>
      <body>
        <header className="site-header ground-label">
          <SiteNav />
        </header>
        <main>{children}</main>
        <footer className="site-footer ground-label">
          <div className="wrap">
            <p>
              Data: APPLE MOTS, De Jong et al. 2022, CC BY 4.0,{" "}
              <a href="https://doi.org/10.5281/zenodo.5939726">doi:10.5281/zenodo.5939726</a>
            </p>
            <p>Footage in the examples comes from that dataset.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
