export default {
  plugins: {
    // Tailwind a été retiré du projet : tout le style passe désormais par le
    // design system SCSS (src/styles/). Autoprefixer reste, il n'a jamais eu
    // de rapport avec Tailwind et préfixe le CSS maison.
    autoprefixer: {},
  },
};
