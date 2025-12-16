classdef ROS2Generator < handle
  % This should be a description of the ROS2Generator class.
  %     It's common for programmers to give a code example inside of their
  %     docstring::
  % 
  %         ROS2gen = ROS2Generator(
  %                 mpc_specification = mpc,
  %                 package_name = name,
  %                 ros2_options= ros2_options,
  %         )
  % 
  %     Here is a link to :py:meth:`__init__`.
  %     
  properties
    parent
  end
  methods
    function obj = ROS2Generator(varargin)
      % Initialize ROS package generator for Impact MPC object
      % Arguments: mpc_specification, ros2_options, kwargs
      % 
      %         :param mpc_specification: Impact MPC object
      %         :type name: MPC
      % 
      %         :param ros2_options: Options regarding the generated ROS 2 executables
      %         :type ros2_options: dictionary
      % 
      %         :param package_name: Name of the ROS 2 package
      %         :type package_name: string
      % 
      %         :param version: Version of the ROS 2 package
      %         :type version: string
      % 
      %         :param description: Description of the ROS 2 package
      %         :type description: string
      % 
      %         :param maintainer: Information of the maintainer of the ROS 2 package
      %         :type maintainer: dictionary
      % 
      %         :param license: License of the ROS 2 package
      %         :type license: string
      % 
      %         :param author: Information of the author of the ROS 2 package
      %         :type author: dictionary
      % 
      %         :param impact_node_name: Name of the Impact node in the ROS 2 package
      %         :type impact_node_name: string
      %         
      if length(varargin)==1 && ischar(varargin{1}) && strcmp(varargin{1},'from_super'),return,end
      if length(varargin)==1 && isa(varargin{1},'py.impact.artifact_ros.ROS2Generator')
        obj.parent = varargin{1};
        return
      end
      global pythoncasadiinterface
      if isempty(pythoncasadiinterface)
        pythoncasadiinterface = impact.PythonCasadiInterface;
      end
      [args,kwargs] = pythoncasadiinterface.matlab2python_arg(varargin,2,{'mpc_specification','ros2_options','kwargs'});
      if isempty(kwargs)
        obj.parent = py.impact.ROS2Generator(args{:});
      else
        obj.parent = py.impact.ROS2Generator(args{:},pyargs(kwargs{:}));
      end
    end
    function [] = delete(obj)
      obj.parent = 0;
      py.gc.collect();
    end
    function varargout = generate_package_xml(obj,varargin)
      global pythoncasadiinterface
      [args,kwargs] = pythoncasadiinterface.matlab2python_arg(varargin,0,{});
      if isempty(kwargs)
        res = obj.parent.generate_package_xml(args{:});
      else
        res = obj.parent.generate_package_xml(args{:},pyargs(kwargs{:}));
      end
      varargout = pythoncasadiinterface.python2matlab_ret(res);
    end
    function varargout = generate_CMakeLists(obj,varargin)
      global pythoncasadiinterface
      [args,kwargs] = pythoncasadiinterface.matlab2python_arg(varargin,0,{});
      if isempty(kwargs)
        res = obj.parent.generate_CMakeLists(args{:});
      else
        res = obj.parent.generate_CMakeLists(args{:},pyargs(kwargs{:}));
      end
      varargout = pythoncasadiinterface.python2matlab_ret(res);
    end
    function varargout = generate_controller_node_cpp(obj,varargin)
      global pythoncasadiinterface
      [args,kwargs] = pythoncasadiinterface.matlab2python_arg(varargin,0,{});
      if isempty(kwargs)
        res = obj.parent.generate_controller_node_cpp(args{:});
      else
        res = obj.parent.generate_controller_node_cpp(args{:},pyargs(kwargs{:}));
      end
      varargout = pythoncasadiinterface.python2matlab_ret(res);
    end
    function varargout = generate_model_node_cpp(obj,varargin)
      global pythoncasadiinterface
      [args,kwargs] = pythoncasadiinterface.matlab2python_arg(varargin,0,{});
      if isempty(kwargs)
        res = obj.parent.generate_model_node_cpp(args{:});
      else
        res = obj.parent.generate_model_node_cpp(args{:},pyargs(kwargs{:}));
      end
      varargout = pythoncasadiinterface.python2matlab_ret(res);
    end
    function varargout = export_package(obj,varargin)
      global pythoncasadiinterface
      [args,kwargs] = pythoncasadiinterface.matlab2python_arg(varargin,0,{'directory'});
      if isempty(kwargs)
        res = obj.parent.export_package(args{:});
      else
        res = obj.parent.export_package(args{:},pyargs(kwargs{:}));
      end
      varargout = pythoncasadiinterface.python2matlab_ret(res);
    end
  end
end
