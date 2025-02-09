from views.base.base_views import AuthBaseHandler
from common.exception import ClientError, ERROR_CODE_0
from models.album_model import Album, Photo
from service.validator import validate_album_name, validate_album_description
from service.image_utils import save_images
from conf.base import SERVER_CONFIGS


class AlbumHandler(AuthBaseHandler):

    def get(self, album_id):
        """
        @api {get} /album/:album_id Get user's albums
        @apiVersion 0.0.1
        @apiGroup Album
        @apiDescription Get user's albums

        @apiParam {Number} [album_id] Album's id
        @apiQuery {Number} [user_id] User's id

        @apiSuccessExample {json} response:
            [
                {
                    id: int,
                    name: string,
                    description: string?,
                    cover: string?
                }
                ...
            ]
        """
        user_id = self.get_argument('user_id', None) or self.current_user.id

        if album_id:
            album = Album.query.filter(Album.id == album_id, ~Album.deleted).first()
            if not album: raise ClientError('album 不存在: %r' % album_id)
            self.success(self._to_json(album))
        else:
            albums = Album.query.filter(Album.user_id == user_id, ~Album.deleted).all()
            albums_json = [self._to_json(album) for album in albums]
            self.success(albums_json)

    def post(self, album_id):
        """
        @api {post} /album/:album_id Update or Add user's albums
        @apiVersion 0.0.1
        @apiGroup Album
        @apiDescription Update or Add user's albums

        @apiParam {Number} [album_id] Album's id
        @apiBody {Number} [user_id] User's id
        @apiBody {String} name Album's name
        @apiBody {String} description Album's description

        @apiSuccess {Object} data Album info
        """
        user_id = self.get_argument('user_id', None) or self.json_args.get('user_id', None) or self.current_user.id
        name = self.get_argument('name', None) or self.json_args.get('name', None)
        description = self.get_argument('description', None) or self.json_args.get('description', None)
        image_metas = self.request.files.get('images', None)
        image = image_metas[0] if image_metas else None

        if album_id:
            self._update(user_id, album_id, name, description, image)
        else:
            self._add(user_id, name, description, image)

    def delete(self, album_id):
        """
        @api {delete} /album/:album_id Delete user's albums
        @apiVersion 0.0.1
        @apiGroup Album
        @apiDescription Delete user's albums

        @apiParam {Number} album_id Album's id
        @apiQuery {Number} [user_id] User's id

        @apiSuccess {Boolean} data success or fail
        """
        if not album_id: raise ClientError('参数缺失: album_id')
        user_id = self.get_argument('user_id', None) or self.current_user.id
        album = Album.query.filter(Album.id == album_id, Album.user_id == user_id).first()
        album.deleted = True
        album.save()
        self.simpleSuccess()

    def _add(self, user_id, name, description, image):
        """
        新增
        :param name:
        :return:
        """
        is_valid, msg = validate_album_name(name)
        if not is_valid: raise ClientError(msg)
        is_valid, msg = validate_album_description(description)
        if not is_valid: raise ClientError(msg)

        count = Album.query.filter(Album.user_id == user_id).count()
        if count >= SERVER_CONFIGS['album_count_limit']: raise ClientError('每个用户最多创建20个相册')

        album = Album.query.filter(Album.user_id == user_id,
                                   Album.name == name,
                                   ~Album.deleted).first()
        if album: raise ClientError('相册已存在: %r' % name)

        album = Album(name=name, description=description, user_id=user_id, cover=save_images(user_id, [image])[0] if image else None)
        album.save()
        self.success(self._to_json(album))

    def _update(self, user_id, album_id, name, description, image):
        """
        修改
        :param name:
        :param album_id:
        :return:
        """
        if not album_id: raise ClientError('参数缺失: album_id')
        album = Album.query.filter(Album.id == album_id, ~Album.deleted, Album.user_id == user_id).first()
        if not album: raise ClientError('相册不存在: %r' % name)

        if name:
            is_valid, msg = validate_album_name(name)
            if not is_valid: raise ClientError(msg)
            album.name = name

        if description:
            is_valid, msg = validate_album_description(description)
            if not is_valid: raise ClientError(msg)
            album.description = description

        if image:
            album.cover = save_images(user_id, [image])[0]

        album.save()
        self.success(self._to_json(album))

    def _to_json(self, album):
        if not album.cover:
            photo = Photo.query.filter(Photo.album_id == album.id, ~Photo.deleted).first()
            album.cover = photo.name
        return album.to_json()
