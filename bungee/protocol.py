from construct import Struct, Field, Flag, UBInt8, SBInt8, SBInt16, SBInt32, SBInt64, BFloat32, BFloat64, PascalString, Adapter

PacketID = UBInt8('packet_id')

Bool = Flag
Byte = SBInt8
Short = SBInt16
Int = SBInt32
Long = SBInt64
Float = BFloat32
Double = BFloat64

def ByteArray(name):
	return PascalString(name, length_field=Short('length'), encoding=None)

class StringAdapter(Adapter):
	def _encode(self, obj, context):
		return Container(length=len(obj), data=obj.encode('utf-16-be'))
	def _decode(self, obj, context):
		return obj.data.decode('utf-16-be')

def String(name):
	return StringAdapter(Struct(name,
			Short('length'),
			Field('data', lambda ctx: ctx.length * 2)
		)
	)

def Slot(name):
	return Struct(name,
		Short('id'),
		If(lambda ctx: ctx.id >= 0,
			Embed(Struct('item_information',
						Byte('count'),
						Short('damage'),
						Short('nbt_length'),
						If(lambda ctx: ctx.nbt_length > 0,
							Field('nbt_data', lambda ctx: ctx.nbt_length)
						)
					)
				)
			)
		)

def IntVector(name):
	return Struct(name,
		Int('x'),
		Int('y'),
		Int('z')
	)

class MetadataAdapter(Adapter):
	def _decode(self, obj, context):
		a = {}
		for container in obj:
			key = container.get('key', None)
			value = container.get('value', None)
			if key and value:
				a[key] = value
		return a

def Metadata(name):
	return MetadataAdapter(RepeatUntil(lambda obj, ctx: obj._item == 0x7F, Struct('data',
		UBInt8('_item'),
		If(lambda ctx: ctx._item != 0x7F, Embed(Struct('kv_data',
			Value('key', lambda ctx: ctx._item & 0x1F),
			Value('_type', lambda ctx: ctx._item >> 5),
			Switch('value', lambda ctx: ctx._type,
				{
					0 : Byte('value'),
					1 : Short('value'),
					2 : Int('value'),
					3 : Float('value'),
					4 : String('value'),
					5 : Slot('value'),
					6 : IntVector('value')
				})
			))),
		)))

def ObjectData(name):
	return Struct(name,
		Int('index'),
		If(lambda ctx: ctx.index != 0, Embed(Struct("short_motion",
			Short('x'),
			Short('y'),
			Short('z')
			)))
	)