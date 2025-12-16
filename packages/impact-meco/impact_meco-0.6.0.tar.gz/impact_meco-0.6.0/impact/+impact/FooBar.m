classdef FooBar < handle
  properties
    parent
  end
  methods
    function obj = FooBar(varargin)
      if length(varargin)==1 && ischar(varargin{1}) && strcmp(varargin{1},'from_super'),return,end
      if length(varargin)==1 && isa(varargin{1},'py.impact.FooBar')
        obj.parent = varargin{1};
        return
      end
      global pythoncasadiinterface
      if isempty(pythoncasadiinterface)
        pythoncasadiinterface = impact.PythonCasadiInterface;
      end
      [args,kwargs] = pythoncasadiinterface.matlab2python_arg(varargin,0,{});
      if isempty(kwargs)
        obj.parent = py.impact.FooBar(args{:});
      else
        obj.parent = py.impact.FooBar(args{:},pyargs(kwargs{:}));
      end
    end
    function [] = delete(obj)
      obj.parent = 0;
      py.gc.collect();
    end
  end
end
