classdef FooBaz < handle
  % This should be a description of the MPC class.
  %   It's common for programmers to give a code example inside of their
  %   docstring::
  % 
  %       from impact import MPC
  %       mpc = MPC(T=2.0)
  % 
  %   Here is a link to :py:meth:`__init__`.
  %   
  properties
      parent
  end
  methods
    function obj = FooBaz(varargin)
      obj.parent = py.impact.FooBar();
    end
  end
end
