// Code generated by protoc-gen-go-grpc. DO NOT EDIT.
// versions:
// - protoc-gen-go-grpc v1.2.0
// - protoc             v3.21.4
// source: hub.proto

package generated

import (
	context "context"
	grpc "google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
)

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
// Requires gRPC-Go v1.32.0 or later.
const _ = grpc.SupportPackageIsVersion7

// HubClient is the client API for Hub service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type HubClient interface {
	StartAdvertisementScanning(ctx context.Context, in *HubCommand, opts ...grpc.CallOption) (*HubResponse, error)
	GetTags(ctx context.Context, in *GetTagRequest, opts ...grpc.CallOption) (*GetTagResponse, error)
}

type hubClient struct {
	cc grpc.ClientConnInterface
}

func NewHubClient(cc grpc.ClientConnInterface) HubClient {
	return &hubClient{cc}
}

func (c *hubClient) StartAdvertisementScanning(ctx context.Context, in *HubCommand, opts ...grpc.CallOption) (*HubResponse, error) {
	out := new(HubResponse)
	err := c.cc.Invoke(ctx, "/gateway.Hub/StartAdvertisementScanning", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *hubClient) GetTags(ctx context.Context, in *GetTagRequest, opts ...grpc.CallOption) (*GetTagResponse, error) {
	out := new(GetTagResponse)
	err := c.cc.Invoke(ctx, "/gateway.Hub/GetTags", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// HubServer is the server API for Hub service.
// All implementations must embed UnimplementedHubServer
// for forward compatibility
type HubServer interface {
	StartAdvertisementScanning(context.Context, *HubCommand) (*HubResponse, error)
	GetTags(context.Context, *GetTagRequest) (*GetTagResponse, error)
	mustEmbedUnimplementedHubServer()
}

// UnimplementedHubServer must be embedded to have forward compatible implementations.
type UnimplementedHubServer struct {
}

func (UnimplementedHubServer) StartAdvertisementScanning(context.Context, *HubCommand) (*HubResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method StartAdvertisementScanning not implemented")
}
func (UnimplementedHubServer) GetTags(context.Context, *GetTagRequest) (*GetTagResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetTags not implemented")
}
func (UnimplementedHubServer) mustEmbedUnimplementedHubServer() {}

// UnsafeHubServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to HubServer will
// result in compilation errors.
type UnsafeHubServer interface {
	mustEmbedUnimplementedHubServer()
}

func RegisterHubServer(s grpc.ServiceRegistrar, srv HubServer) {
	s.RegisterService(&Hub_ServiceDesc, srv)
}

func _Hub_StartAdvertisementScanning_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(HubCommand)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(HubServer).StartAdvertisementScanning(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/gateway.Hub/StartAdvertisementScanning",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(HubServer).StartAdvertisementScanning(ctx, req.(*HubCommand))
	}
	return interceptor(ctx, in, info, handler)
}

func _Hub_GetTags_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(GetTagRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(HubServer).GetTags(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/gateway.Hub/GetTags",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(HubServer).GetTags(ctx, req.(*GetTagRequest))
	}
	return interceptor(ctx, in, info, handler)
}

// Hub_ServiceDesc is the grpc.ServiceDesc for Hub service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var Hub_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "gateway.Hub",
	HandlerType: (*HubServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "StartAdvertisementScanning",
			Handler:    _Hub_StartAdvertisementScanning_Handler,
		},
		{
			MethodName: "GetTags",
			Handler:    _Hub_GetTags_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "hub.proto",
}
