# Instagram (@feral_taxonomy)

Cada carpeta de aquí es un post. La Action `Publicar en Instagram` sube **uno**
cada martes y viernes (17:07 UTC), el primero en orden de nombre que no esté en
`publicado.json`, y lo apunta ahí. También se lanza a mano desde la pestaña
Actions.

## Un post

```
content/instagram/05-nombre/
  post.txt
  01.jpg, 02.png …   (opcional)
```

`post.txt`:

```
Proyecto: jiron-tumbes     (opcional: usa las imágenes de ese proyecto)
Imágenes: 2, 1             (opcional: cuáles y en qué orden; si no, todas)

El texto del post, tal cual. Hasta 2.200 caracteres y 30 hashtags.
```

- Si la carpeta tiene imágenes propias, se usan esas y se ignora `Proyecto`.
- 1 imagen → foto; de 2 a 10 → carrusel. Solo imágenes, no vídeo.
- Todas se llevan a la proporción de la primera (entre 4:5 y 1.91:1) con
  relleno blanco. No se recorta nada.
- **Las carpetas que empiezan por `_` son borradores** y no se publican. Para
  aprobar uno, quitarle el `_`.

## Orden

El post tiene que estar **desplegado en la web** antes de publicarse, porque
Instagram baja las imágenes de `sebastianortizdezevallos.com/instagram/…`. Con
hacer push a main basta: el despliegue tarda un par de minutos.

Para ver qué saldría la próxima vez sin publicar: `npm run instagram:prueba`.

## Configuración (una vez)

1. La cuenta de Instagram tiene que ser profesional (Business o Creator).
2. En developers.facebook.com, crear una app con el producto «Instagram API
   with Instagram login», añadir la cuenta y generar un token de acceso con
   `instagram_business_basic` e `instagram_business_content_publish`.
3. En GitHub, Settings > Secrets and variables > Actions, crear `IG_USER_ID` e
   `IG_ACCESS_TOKEN`.

El token dura 60 días. Para renovarlo antes de que caduque:

```
https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=<TOKEN>
```

y pegar el nuevo en el secreto.
